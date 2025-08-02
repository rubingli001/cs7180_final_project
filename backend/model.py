import pymupdf
import pdfplumber
import os
from llama_index.core import Document, VectorStoreIndex
from llama_index.llms.openrouter import OpenRouter
from dotenv import load_dotenv

load_dotenv() 
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenRouter LLM
llm = OpenRouter(
    model="anthropic/claude-sonnet-4", 
    api_key=os.getenv("OPENROUTER_API_KEY"))

# ----------------- PDF extraction ----------------
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


# The helper function to tidy up the row and remove the None values 
def clean_table_row(row):
    cleaned_row = []
    for cell in row:
        # Skip None values or cells that are just a dollar sign
        if cell is None:
            continue

        cell_str = str(cell).strip()
        if cell_str == '$':
            continue

        if cell_str:
            cleaned_row.append(cell_str)

    return cleaned_row


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
                        cleaned_table = [clean_table_row(row) for row in table if clean_table_row(row)]
                        output.append({
                            "type": "table",
                            "content": cleaned_table
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

# ----------------- LlamaIndex Pipeline -----------------
def build_index_from_pdf(pdf_file):
    extracted_data = extract_text_from_pdf(pdf_file)
    documents = []

    for item in extracted_data:
        if item['type'] == 'text':
            documents.append(Document(text=item['content']))
        elif item['type'] == 'table':
            # Convert table rows to a string representation
            table_content = "\n".join(["\t".join(row) for row in item['content']])
            documents.append(Document(text=table_content))

    index = VectorStoreIndex.from_documents(documents)
    return index

def query_index(index: VectorStoreIndex, query: str, llm=llm):
    engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=10,
        max_tokens=4096,
        response_mode="compact")
    response = engine.query(query)
    return str(response)