from core.supabase import supabase

def upload_generated_image(
    file_path: str,
    filename: str,
):
    storage_path = f"chat-images/{filename}"

    try:
        with open(file_path, "rb") as file:
            file_bytes = file.read()

        supabase.storage.from_("airw-documents").upload(
            storage_path,
            file_bytes,
            {
                "content-type": "image/png"
            }
        )

    except Exception as e:
        print("Supabase image upload error:", e)
        raise RuntimeError(
            f"Could not upload generated image: {e}"
        )

    return storage_path


def download_file(
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

        with open(output_path, "wb") as file:
            file.write(file_bytes)

    except Exception as e:
        print("Supabase download error:", e)

        raise RuntimeError(
            f"Could not download file: {e}"
        )

    return output_path