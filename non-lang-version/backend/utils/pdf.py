import fitz

def extract_text(pdf_path):
    document = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(document):
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

        pages.append({
            "page": page_number + 1,
            "text": page_text.strip(),
            "width": page_dict["width"],
            "height": page_dict["height"],
            "spans": spans,
        })

    document.close()
    return pages