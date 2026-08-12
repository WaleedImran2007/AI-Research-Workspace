import fitz
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PDF_PATH = os.path.join(
    CURRENT_DIR, "../uploads/documents/1784371133_Integrity and security.pdf"
)

doc = fitz.open(PDF_PATH)

page = doc[3]

data = page.get_text("dict")
print(data)
doc.close()