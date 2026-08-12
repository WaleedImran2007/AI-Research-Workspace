from dotenv import load_dotenv
load_dotenv()

import os
import io
import ast
import uuid
import re
import contextlib

from schemas.tool_result import ToolResult

from database import documents_collection

from .python_helpers import get_csv_schema

from chains.generate_python_chain import generate_python_chain

from langchain_core.tools import tool

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
    """Generates and executes Python code based on the provided task in the input, optionally using a document for context."""

    task = input.get("task") if input else ""
    return_code = input.get("return_code", False) if input else False
    document_name = input.get("document_name") if input else None

    path = None
    schema = None

    if document_name:
        document = documents_collection.find_one(
            {
                "ownerId": owner_id,
                "originalName": {
                    "$regex": f"^{document_name}$",
                    "$options": "i"
                }
            }
        )

        if document:
            path = os.path.join(
                UPLOAD_FOLDER,
                document["fileName"]
            )

            if document["documentType"] == "csv":
                schema = get_csv_schema(path)
                

    # Ensure output folder exists
    os.makedirs("generated", exist_ok=True)
    filename = f"generated/{uuid.uuid4()}.png"

    print("Filename:", filename)

    if path:
        print("File Path:", path)

    # 1. Fetch raw output from LLM
    raw_code = generate_python_code(task, filename, path, schema)

    # 2. Clean markdown backticks before validation
    code = clean_generated_code(raw_code)

    # 3. Validate code structure via AST
    validate_python_code(code)

    print("\n===== GENERATED PYTHON CODE =====")
    print(code)
    print("=================================\n")

    stdout_buffer = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout_buffer):
            # Pass filename so `plt.savefig(filename)` works inside exec()
            safe_globals = {
                "__builtins__": __builtins__,
                "filename": filename,
                "path": path,
            }

            exec(code, safe_globals)

        output = stdout_buffer.getvalue().strip()

        sources = []
        if path and os.path.exists(path):
            documentName = os.path.basename(path)
            document = documents_collection.find_one({
                "documentName": {
                    "$regex": documentName,
                    "$options": "i"
                }
            })

            document_id = str(document["_id"]) if document else None
            page = document.get("page", 1) if document else 1
            text = document.get("text", "") if document else ""
            filename = document.get("fileName", "") if document else ""

            sources.append({
                "type": "document",
                "documentId": document_id,
                "documentName": documentName,
                "fileName": filename,
                "page": page,
                "text": text,
            })

        if os.path.exists(filename):
            sources.append({
                "type": "image",
                "path": filename,
            })

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
                "The requested graph has been generated successfully and is attached below."
                if "plt.savefig(filename)" in code
                else ""
            )

            llm_context = f"""
                A Python program successfully completed the following task:

                Task: {task}

                Output:
                {output if output else '(No text output)'}

                {graph_note}
            """

            print("LLM Context:", llm_context)

        return ToolResult(
            llm_context=llm_context,
            sources=sources or [],
        )

    except Exception as e:
        import traceback
        traceback.print_exc()

        return ToolResult(
            llm_context=f"Python Error:\n\n{str(e)}",
            sources=[],
        )
