import streamlit as st
import json
import re
from datetime import datetime
from backend.model_docling import query_index
from llama_index.core import Document, VectorStoreIndex
from llama_index.llms.openrouter import OpenRouter
from dotenv import load_dotenv
import os
#----------Define the LLM specific for the front page----------
load_dotenv()
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
llm = OpenRouter(
    model="anthropic/claude-sonnet-4", 
    api_key=os.getenv("OPENROUTER_API_KEY"))

# ----------------- Extract Key Metrics ----------------

def extract_key_metrics(index: VectorStoreIndex):
    # Find the company name first
    company_name = find_company_name_from_index(index)
    # Metrics extraction logic
    metrics_schema = {
        "company_name": company_name if company_name else "string (company name)",
        "fiscal_year":"string (YYYY)",
        "assets": "float",
        "revenue": {"current": "float", "previous": "float"},
        "net_profit": {"current": "float", "previous": "float"},
        "profit_margin": {"current": "float", "previous": "float"},
        "eps": {"current": "float", "previous": "float"},
    }
    try:
        # Use the RAG system to extract key metrics
        prompt = f"""
You are a financial analysis assistant.
Extract the following metrics from the document.

SEARCH THOROUGHLY across ALL document sections for:
- Company name in headers, footers, titles or letterheads
- Fiscal year periods (look for "fiscal 2024", "year ended", reporting periods)
- Revenue/net sales figures for current and prior year (in millions)
- Net income/profit for current and prior year (in millions)
- Profit margin percentages (net, gross, or operating margins)
- Earnings per share (EPS) for current and prior year
- Total assets for current year (Look specifically in the section titled "Balance Sheet", in millions)

Return ONLY valid JSON matching exactly this structure:
{json.dumps(metrics_schema, indent=2)}

Rules:
- Numbers must be numeric values (no $ signs, %, or commas).
- If "company_name" in the JSON already has a value, DO NOT modify it.
- Use null if data is not available.
        """
        response = query_index(index, prompt,llm=llm)
        # Extract JSON from the response
        metrics_json = extract_json_from_response(response)
        print(f"📊 Extracted metrics: {metrics_json}")
        if not metrics_json:
            st.warning("⚠️ LLM response could not be parsed as JSON. Returning empty metrics.")
            return {}
        
        return metrics_json
       
    except Exception as e:
        st.error(f"Error extracting key metrics: {str(e)}")
        return {}

# ----------------- Extract Risk Factors ----------------
def extract_risk_factors(index: VectorStoreIndex):
    # Use the RAG system to extract key metrics
    prompt = """
    You are a financial analysis assistant.
    Task: Identify and summarize the most significant business highlights, changes or achievements. 
    Rules: 
    - Include quantitative data if available in the document.
    - Include details specific to the company, not generic risks.
    """
    response = query_index(index, prompt, llm=llm)
    print(f"⚠️ Extracted risk factors: {response}")
    return str(response)



# ----------------- Helper Functions ----------------
def extract_json_from_response(response_text):
    """Extract valid JSON from LLM response text."""
    try:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return None


def find_company_name_from_index(index):
    """Scan entire document text for company name patterns."""
    docs = index.docstore.docs
    
    # Combine all node text into one string
    full_text = " ".join([doc.text for doc in docs.values()])
    
    # Regex for common company suffixes
    pattern = r"((?:#+\s*)?[A-Z][A-Za-z& ]+(Inc\.|Corporation|Corp\.|Ltd\.|Co\.|PLC|p\.l\.c\.|S\.A\.|N\.V\.))"
    match = re.search(pattern, full_text)
    cleaned_name = re.sub(r"#", "", match.group(0)).strip()
    return cleaned_name if match else None