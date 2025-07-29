import streamlit as st
from datetime import datetime
from backend.model import build_index_from_pdf
from backend.model_docling import build_index_from_pdf_docling
from backend.utils import extract_key_metrics
import tempfile

# Configure page
st.set_page_config(
    page_title="Financial Statement Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Custom title styling */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Analysis cards */
    .analysis-card {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #3b82f6;
        margin-bottom: 1.5rem;
        height: 100%;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    
    .card-content {
        line-height: 1.6;
        color: #475569;
    }
    
    /* Sidebar logo */
    .sidebar-logo {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
                
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'file_content' not in st.session_state:
    st.session_state.file_content = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'key_metrics' not in st.session_state:
    st.session_state.key_metrics = None


# Sidebar
with st.sidebar:
    
    # Upload section
    st.markdown("### 📁 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a financial document",
        type=['pdf', 'txt'],
        help="Upload 10-K filings, earnings releases, or other financial documents",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✅ **{uploaded_file.name}**")
        st.info(f"📄 {uploaded_file.size:,} bytes • Processing...")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name
        
        with st.spinner("🔄 Analyzing document..."):
                # Build Index from the document
                st.session_state.index = build_index_from_pdf_docling(temp_file_path)

                # Extract key metrics using RAG pipeline
                st.session_state.key_metrics = extract_key_metrics(st.session_state.index)
                st.success("✅ Document processed for Q&A!")
    

# Main content

# Welcome screen
st.markdown('<h1 class="main-title">📊 Financial Statement Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyze 10-K filings, financial statements and earnings releases with AI-powered insights</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
tab1, tab2 = st.tabs(["📋 Company Financial Overview", "💬 Q&A Chat"])

with col1:
    st.markdown("""
    <div class="analysis-card">
        <div class="card-title">📁 Upload</div>
        <div class="card-content">
            • Support for PDF and text files<br>
            • 10-K filings and earnings releases<br>
            • Automatic text extraction<br>
            • Secure document processing
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="analysis-card">
        <div class="card-title">🔍 Analyze</div>
        <div class="card-content">
            • AI-powered document analysis<br>
            • Key metrics extraction<br>
            • Risk and opportunity identification<br>
            • Financial performance insights
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="analysis-card">
        <div class="card-title">💬 Q&A</div>
        <div class="card-content">
            • Interactive chat interface<br>
            • Ask questions about documents<br>
            • Get detailed explanations<br>
            • Financial metric clarifications
        </div>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.uploaded_file:
    st.info("👈 **Upload a financial document using the sidebar to get started!**")

# Show the key metrics if available
if st.session_state.key_metrics:
    metrics = st.session_state.key_metrics
    st.markdown("#### 🏢 Company Information")
    st.markdown(f"""
    <div class="analysis-card">
        <div class="card-content">
            <strong>Company Name:</strong> {metrics.get('company_name', 'N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 📅 Fiscal Period")
    st.markdown(f"""
    <div class="analysis-card">
        <div class="card-content">
            <strong>Fiscal Year:</strong> {metrics.get('fiscal_year', 'N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 💰 Financial Position")
    st.markdown(f"""
    <div class="analysis-card">
        <div class="card-content">
            <strong>Brief Financial Overview:</strong> {metrics.get('assets', 'N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 📊 Profitability Status")
    profitability = metrics.get('profitability', 'N/A')
    if 'profit' in profitability.lower() or 'positive' in profitability.lower():
        status_icon = "✅"
    elif 'loss' in profitability.lower() or 'deficit' in profitability.lower():
        status_icon = "❌"
    else:
        status_icon = "⚠️"
    
    st.markdown(f"""
    <div class="analysis-card">   
        <strong>Status:</strong>
        <span style = "color: #475569">{status_icon}{profitability}</span>
    </div>
    """, unsafe_allow_html=True)
    
