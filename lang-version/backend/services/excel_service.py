import re
import ast

from core.supabase import supabase

ALLOWED_IMPORTS = {
    "openpyxl",
}

def download_excel(
    stored_filename: str,
    output_path: str
):
    storage_path = f"documents/{stored_filename}"

    try:
        file_bytes = (
            supabase.storage
            .from_("airw-documents")
            .download(storage_path)
        )
    except Exception as e:
        print("Supabase download error:", e)
        raise RuntimeError(
            f"Could not download Excel file: {e}"
        )

    with open(output_path, "wb") as file:
        file.write(file_bytes)

    return output_path

def upload_excel(
    file_path: str,
    stored_filename: str
):
    storage_path = f"chat-documents/{stored_filename}"

    try:
        with open(file_path, "rb") as file:
            file_bytes = file.read()

        supabase.storage.from_("airw-documents").upload(
            storage_path,
            file_bytes,
            {
                "content-type": (
                    "application/vnd.openxmlformats-officedocument"
                    ".spreadsheetml.sheet"
                )
            }
        )

    except Exception as e:
        print("Supabase upload error:", e)
        raise RuntimeError(
            f"Could not upload modified Excel file: {e}"
        )

    return storage_path

def inspect_excel(wb):
    workbook_info = []

    for sheet in wb.worksheets:
        sheet_info = {
            "sheet_name": sheet.title,
            "max_row": sheet.max_row,
            "max_column": sheet.max_column,
            "headers": [],
            "sample_rows": []
        }

        # GET HEADERS
        for cell in sheet[1]:
            sheet_info["headers"].append(cell.value)

        # GET FIRST 5 ROWS OF DATA (EXCLUDING HEADER)
        for row in sheet.iter_rows(
            min_row = 2,
            max_row = min(6, sheet.max_row),
            values_only = True
        ):
            sheet_info["sample_rows"].append(row)

        workbook_info.append(sheet_info)

    return workbook_info

def clean_generated_code(code: str) -> str:
    """
    Clean the generated Python code by removing any Markdown code fences
    and ensuring it is valid Python code.
    """

    cleaned = code.strip()

    match = re.search(
        r"^```(?:python)?\s*\n(.*?)\n?```$",
        cleaned,
        re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return cleaned

def validate_excel_code(code: str):
    tree = ast.parse(code)

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split('.')[0]

                if module not in ALLOWED_IMPORTS:
                    raise Exception(f"Import '{alias.name}' is not allowed.")

        if isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split(".")[0]

                if module not in ALLOWED_IMPORTS:
                    raise Exception(
                        f"Import from '{node.module}' is not allowed."
                    )

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in {
                    "eval",
                    "exec",
                    "open",
                    "input",
                    "__import__",
                    "compile",
                    "breakpoint"
                }:
                    raise Exception(f"Function '{node.func.id}' is not allowed.")
