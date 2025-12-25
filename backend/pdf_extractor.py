import fitz  # PyMuPDF

def extract_pdf_data(pdf_path):
    doc = fitz.open(pdf_path)
    all_text_elements = []

    for page in doc:
        # Sort=True is key for reflowable sequence
        blocks = page.get_text("dict", sort=True)["blocks"]
        
        for b in blocks:
            if b["type"] == 0:  # Text type
                for line in b["lines"]:
                    for span in line["spans"]:
                        all_text_elements.append({
                            "text": span["text"],
                            "size": round(span["size"], 1),
                            "flags": span["flags"]
                        })
    doc.close()
    return all_text_elements