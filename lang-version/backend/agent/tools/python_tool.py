import shutil

from dotenv import load_dotenv
load_dotenv()

import os
import io
import ast
import uuid
import re
import contextlib
import tempfile

from schemas.tool_result import ToolResult

from database import documents_collection

from .python_helpers import get_csv_schema

from chains.generate_python_chain import generate_python_chain

from langchain_core.tools import tool

from services.python_service import (
    upload_generated_image,
    download_file
)

# Included all libraries permitted in the system prompt
ALLOWED_IMPORTS = {
    "math",
    "statistics",
    "random",
    "itertools",
    "datetime",
    "json",
    "re",
    "numpy",
    "pandas",
    "matplotlib"
}

BLOCKED_FUNCTIONS = {
    "eval",
    "exec",
    "open",
    "input",
    "__import__",
    "compile",
    "breakpoint"
}

UPLOAD_FOLDER = "uploads/documents"


def clean_generated_code(code: str) -> str:
    """Strips Markdown backticks (```python ... ```) if the LLM includes them."""
    cleaned = code.strip()
    # Match ```python <code> ``` or ``` <code> ```
    match = re.search(r"^```(?:python)?\s*\n?(.*?)\n?```$", cleaned, re.DOTALL)
    if match:
        return match.group(1).strip()
    return cleaned


def validate_python_code(code: str):
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split('.')[0]
                if module not in ALLOWED_IMPORTS:
                    raise Exception(f"Import '{alias.name}' is not allowed.")

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split('.')[0]
                if module not in ALLOWED_IMPORTS:
                    raise Exception(f"Import '{node.module}' is not allowed.")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_FUNCTIONS:
                raise Exception(f"Function '{node.func.id}' is not allowed.")


def generate_python_code(task: str, filename: str, path: str = None, schema: dict = None) -> str:
    schema_text = ""

    if schema:
        schema_text = f"""
            File Type: CSV

            Columns:

            {", ".join(schema["columns"])}

            Preview (first rows):

            {schema["preview"]}

            Column Types:

            {schema["dtypes"]}
        """

    response = generate_python_chain.invoke(
        {
            "task": task,
            "filename": filename,
            "path": path,
            "schema": schema_text
        }
    )

    return response.content


@tool
def python_tool(filters, owner_id, input=None) -> ToolResult:
    """Generates and executes Python code based on the provided task in the input,
    optionally using a document for context.
    """

    task = input.get("task") if input else ""
    return_code = input.get("return_code", False) if input else False
    document_name = input.get("document_name") if input else None

    os.makedirs("generated", exist_ok=True)

    # ---------------------------------------------------------
    # Variables
    # ---------------------------------------------------------

    path = None
    schema = None
    document = None

    # Generated image path
    filename = os.path.join(
        "generated",
        f"{uuid.uuid4()}.png"
    )

    print("Generated Output Path:", filename)

    # ---------------------------------------------------------
    # Find document
    # ---------------------------------------------------------

    if document_name:

        document = documents_collection.find_one(
            {
                "ownerId": owner_id,
                "originalName": {
                    "$regex": f"^{re.escape(document_name)}$",
                    "$options": "i"
                }
            }
        )

        if not document:
            return ToolResult(
                llm_context=(
                    f"Could not find the document "
                    f"'{document_name}'."
                ),
                sources=[]
            )

        print(
            "Found Document:",
            document.get("originalName")
        )

        # -----------------------------------------------------
        # Download document from Supabase
        # -----------------------------------------------------

        document_type = document.get("documentType")
        stored_filename = document.get("fileName")

        if not stored_filename:
            return ToolResult(
                llm_context=(
                    f"Document '{document_name}' does not have "
                    f"a stored filename."
                ),
                sources=[]
            )

        # Create a temporary directory for downloaded files
        temp_dir = tempfile.mkdtemp(
            prefix="airw_python_"
        )

        path = os.path.join(
            temp_dir,
            stored_filename
        )

        try:

            print(
                "Downloading document from Supabase:",
                stored_filename
            )

            download_file(
                stored_filename=stored_filename,
                output_path=path
            )

            print(
                "Downloaded document to:",
                path
            )

        except Exception as e:

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )

            return ToolResult(
                llm_context=(
                    f"Could not download document "
                    f"'{document_name}': {str(e)}"
                ),
                sources=[]
            )

        # -----------------------------------------------------
        # Get CSV schema
        # -----------------------------------------------------

        if document_type == "csv":

            try:
                schema = get_csv_schema(path)

                print(
                    "CSV Schema:",
                    schema
                )

            except Exception as e:

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )

                return ToolResult(
                    llm_context=(
                        f"Could not inspect CSV document "
                        f"'{document_name}': {str(e)}"
                    ),
                    sources=[]
                )

    else:
        temp_dir = None

    # ---------------------------------------------------------
    # Generate Python code
    # ---------------------------------------------------------

    try:

        raw_code = generate_python_code(
            task=task,
            filename=filename,
            path=path,
            schema=schema
        )

        # -----------------------------------------------------
        # Clean generated code
        # -----------------------------------------------------

        code = clean_generated_code(
            raw_code
        )

        # -----------------------------------------------------
        # Validate generated code
        # -----------------------------------------------------

        validate_python_code(
            code
        )

        print(
            "\n===== GENERATED PYTHON CODE ====="
        )

        print(code)

        print(
            "=================================\n"
        )

        # -----------------------------------------------------
        # Execute generated code
        # -----------------------------------------------------

        stdout_buffer = io.StringIO()

        with contextlib.redirect_stdout(
            stdout_buffer
        ):

            safe_globals = {
                "__builtins__": __builtins__,
                "filename": filename,
                "path": path,
            }

            exec(
                code,
                safe_globals
            )

        output = stdout_buffer.getvalue().strip()

        # -----------------------------------------------------
        # Sources
        # -----------------------------------------------------

        sources = []

        # -----------------------------------------------------
        # Document source
        # -----------------------------------------------------

        if document:

            sources.append(
                {
                    "type": "document",

                    "documentId": str(
                        document["_id"]
                    ),

                    "documentName": document.get(
                        "originalName",
                        ""
                    ),

                    "fileName": document.get(
                        "fileName",
                        ""
                    ),

                    "page": document.get(
                        "page",
                        1
                    ),

                    "text": document.get(
                        "text",
                        ""
                    ),
                }
            )

        # -----------------------------------------------------
        # Generated image
        # -----------------------------------------------------

        if os.path.exists(filename):

            generated_image_filename = (
                os.path.basename(filename)
            )

            print(
                "Generated image found:",
                filename
            )

            # Upload image to Supabase
            upload_generated_image(
                file_path=filename,
                filename=generated_image_filename
            )

            print(
                "Generated image uploaded to Supabase:",
                generated_image_filename
            )

            # Add image as a source
            sources.append(
                {
                    "type": "image",
                    "path": generated_image_filename,
                }
            )

        # -----------------------------------------------------
        # LLM Context
        # -----------------------------------------------------

        if return_code:

            llm_context = f"""
                The requested Python code has been generated successfully.

                Python Code:

                ```python
                {code}
                ```

                Output:
                {output if output else '(No text output)'}
            """

        else:

            graph_note = (
                "The requested graph has been generated successfully "
                "and is attached below."
                if os.path.exists(filename)
                else ""
            )

            llm_context = f"""
                A Python program successfully completed the following task:

                Task: {task}

                Output:
                {output if output else '(No text output)'}

                {graph_note}
            """

        print(
            "LLM Context:",
            llm_context
        )

        # -----------------------------------------------------
        # Return ToolResult
        # -----------------------------------------------------

        return ToolResult(
            llm_context=llm_context,
            sources=sources
        )

    except Exception as e:

        import traceback

        traceback.print_exc()

        return ToolResult(
            llm_context=(
                f"Python Error:\n\n{str(e)}"
            ),
            sources=[]
        )

    finally:

        # -----------------------------------------------------
        # Cleanup downloaded document
        # -----------------------------------------------------

        if temp_dir:

            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )