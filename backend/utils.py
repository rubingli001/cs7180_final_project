import streamlit as st
from datetime import datetime
from backend.model import build_index_from_pdf, query_index
from backend.model_docling import build_index_from_pdf_docling
from llama_index.core import Document, VectorStoreIndex

# ----------------- Extract Key Metrics ----------------
def extract_key_metrics(index: VectorStoreIndex):
    # Example metrics extraction logic
    """Extract key financial metrics from the document"""
    metrics = {
        "company_name": "N/A",
        "fiscal_year":"N/A",
        "assets": "N/A",
        "profitability": "N/A",
    }
    try:
        # Use the RAG system to extract key metrics
        metric_questions = [
            "What is the company name?",
            "What are the fiscal years in the document?",
            "What are the total assets, revenue, gross profit and net profit?",
            "What is the profitablity status?",
        ]
        returned_metrics = []
        for question in metric_questions:
            response = query_index(index, question)
            if response:
                returned_metrics.append(response.strip())

        # Parse responses
        if returned_metrics:
            metrics["company_name"] = returned_metrics[0]
            metrics["fiscal_year"] = returned_metrics[1]
            metrics["assets"] = returned_metrics[2]
            metrics["profitability"] = returned_metrics[3]
    except Exception as e:
        st.error(f"Error extracting key metrics: {str(e)}")
    
    return metrics