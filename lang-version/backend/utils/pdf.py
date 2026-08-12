import fitz
from langchain_core.documents import Document

def extract_text(pdf_path):
    pdf = fitz.open(pdf_path)
    documents = []

    for page_number, page in enumerate(pdf):
        page_dict = page.get_text("dict")

        page_text = ""
        spans = []

        for block in page_dict["blocks"]:
            if block["type"] != 0:  # Skip non-text blocks
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    page_text += text + " "

                    spans.append({
                        "text": text,
                        "bbox": span["bbox"],
                    })

        documents.append(
            Document(
                page_content=page_text.strip(),
                metadata={
                    "page": page_number + 1,
                    "width": page_dict["width"],
                    "height": page_dict["height"],
                    "spans": spans,
                }
            ))

    pdf.close()
    return documents