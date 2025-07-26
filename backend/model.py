import pymupdf
import pdfplumber


def likely_contains_table(text):
    """Heuristic to determine if a page likely contains a table based on text structure."""
    # Keyword-based detection
    FINANCIAL_KEYWORDS = [
        'following table', 'following tables', 'as follows', 'consolidated', 'balance sheet', 
        'income statement', 'cash flows', 'assets', 
        'liabilities', 'net income', 'revenues', 'expenses'
    ]
    if any(keyword in text.lower() for keyword in FINANCIAL_KEYWORDS):
        return True
    # Pattern-based detection
    lines = text.splitlines()
    count = sum(
        1 for line in lines
        if any(sym in line for sym in ['$','%']) and any(char.isdigit() for char in line)
    )
    return count >=2


def extract_text_from_pdf(pdf_file):
    output = []

    # open PDF file
    try:
        pymupdf_doc = pymupdf.open(pdf_file)
        with pdfplumber.open(pdf_file) as plumber_doc:
            for pymupdf_page, plumber_page in zip(pymupdf_doc, plumber_doc.pages):
                text = pymupdf_page.get_text()

                if likely_contains_table(text):
                    # Use PDFPlumber to extract full page text if the page likely contains a table
                    full_text = plumber_page.extract_text()
                    if full_text:
                        output.append({
                            "type": "text",
                            "content": full_text.strip()
                        })

                    tables = plumber_page.extract_tables()
                    for table in tables:
                        output.append({
                            "type": "table",
                            "content": table
                        })
                # Use PyMuPDF for faster text extraction if no table is detected
                else:
                    output.append({
                        "type": "text",
                        "content": text.strip()
                    })
        return output
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

    
