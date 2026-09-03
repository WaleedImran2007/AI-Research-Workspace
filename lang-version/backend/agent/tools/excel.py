from langchain_core.tools import tool

from schemas.tool_result import ToolResult, ToolFile

from chains.generate_excel_chain import generate_excel_chain

from database import documents_collection

import os

from openpyxl import load_workbook

import uuid

from services.excel_service import (
    download_excel,
    upload_excel,
    inspect_excel,
    clean_generated_code,
    validate_excel_code
)


def find_excel_document(
    original_name: str,
    owner_id: str
):
    document = documents_collection.find_one({
        "originalName": original_name,
        "ownerId": owner_id
    })

    return document["fileName"] if document else None


@tool
def excel_tool(
    owner_id: str,
    input=None
) -> ToolResult:
    """
    Execute an Excel automation task using dynamically generated
    and validated Python code.
    """

    file_name = input.get("file_name") if input else None
    task = input.get("task") if input else None

    print("Original file:", file_name)
    print("Task:", task)
    print("Owner ID:", owner_id)

    # 1. Validate input

    if not file_name:
        return ToolResult(
            llm_context="No Excel file name was provided.",
            sources=[]
        )

    if not task:
        return ToolResult(
            llm_context="No Excel task was provided.",
            sources=[]
        )

    try:

        # 2. Find the actual stored filename

        stored_filename = find_excel_document(
            original_name=file_name,
            owner_id=owner_id
        )

        if stored_filename is None:
            return ToolResult(
                llm_context=(
                    f"Excel file '{file_name}' "
                    "was not found."
                ),
                sources=[]
            )

        print("Stored filename:", stored_filename)

        # 3. Download original Excel file

        os.makedirs("temp", exist_ok=True)

        input_file = f"temp/{stored_filename}"

        download_excel(
            stored_filename=stored_filename,
            output_path=input_file
        )

        print("Downloaded file:", input_file)

        # 4. Load workbook

        wb = load_workbook(input_file)

        print("Workbook loaded successfully.")

        # 5. Inspect workbook

        workbook_context = inspect_excel(wb)

        print("WORKBOOK CONTEXT:")
        print(workbook_context)

        # 6. Generate Python code

        response = generate_excel_chain.invoke({
            "filename": stored_filename,
            "workbook_context": workbook_context,
            "task": task
        })

        generated_code = response.content

        print("GENERATED CODE:")
        print(generated_code)

        # 7. Clean generated code

        generated_code = clean_generated_code(
            generated_code
        )

        print("CLEANED CODE:")
        print(generated_code)

        # 8. Validate generated code

        try:
            validate_excel_code(
                generated_code
            )

            print("CODE VALIDATION PASSED")

        except SyntaxError as e:

            print("AST SYNTAX VALIDATION FAILED:", e)

            return ToolResult(
                llm_context=(
                    "The generated Excel code "
                    "contains invalid Python syntax."
                ),
                sources=[]
            )

        except Exception as e:

            print("AST VALIDATION FAILED:", e)

            return ToolResult(
                llm_context=(
                    "The generated Excel code "
                    f"was rejected for security reasons: {str(e)}"
                ),
                sources=[]
            )

        # 9. Execute generated code

        try:
            exec(
                generated_code,
                { "wb": wb }
            )

            print("CODE EXECUTED SUCCESSFULLY.")

        except Exception as e:

            print("GENERATED CODE EXECUTION FAILED: ", e)

            return ToolResult(
                llm_context=(
                    "The Excel task could not be completed "
                    f"because the generated code failed during "
                    f"execution: {str(e)}"
                ),
                sources=[]
            )

        # 10. Save modified workbook

        output_filename = (f"modified_{uuid.uuid4()}_{stored_filename}")

        output_file = (f"temp/{output_filename}")

        wb.save(output_file)

        print("MODIFIED FILE SAVED: ", output_file)

        # 11. Upload modified workbook

        upload_excel(
            file_path=output_file,
            stored_filename=output_filename
        )

        print("MODIFIED FILE UPLOADED SUCCESSFULLY.")

        # 12. Return ToolResult

        return ToolResult(
            llm_context=(
                f"Successfully completed the Excel task: "
                f"{task}"
            ),
            sources=[],
            file=ToolFile(
                filename=output_filename,
                file_type="xlsx",
                storage_path=f"documents/{output_filename}"
            )
        )

    # General exceptions

    except KeyError as e:

        return ToolResult(
            llm_context=(
                f"Missing required parameter: "
                f"{e.args[0]}"
            ),
            sources=[]
        )

    except Exception as e:

        print("EXCEL TOOL FAILED:", e)

        return ToolResult(
            llm_context=(
                f"Excel operation failed: {str(e)}"
            ),
            sources=[]
        )