import sys
import pdfplumber

def extract_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

if __name__ == "__main__":
    pdf_path = sys.argv[1]
    print(extract_text(pdf_path))
