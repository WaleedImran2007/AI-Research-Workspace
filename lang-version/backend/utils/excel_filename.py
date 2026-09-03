from pathlib import Path
from uuid import uuid4


def generate_modified_filename(original_filename: str) -> str:
    """
    Generate a unique filename for an assistant-modified Excel file.
    """

    path = Path(original_filename)

    unique_id = uuid4().hex

    return (
        f"{unique_id}_"
        f"{path.stem}_modified"
        f"{path.suffix}"
    )