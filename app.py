import streamlit as st
from datetime import datetime
import PyPDF2
import io

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

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None


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
        
        # Process file
        if uploaded_file.type == "application/pdf":
            content = extract_text_from_pdf(uploaded_file)
        else:
            content = uploaded_file.read().decode('utf-8')
        
        if content:
            st.session_state.file_content = content
            with st.spinner("🔄 Analyzing document..."):
                # Simulate analysis (replace with actual analysis logic)
                st.success("✅ Analysis Complete!")
    

    
# Main content

# Welcome screen
st.markdown('<h1 class="main-title">📊 Financial Statement Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyze 10-K filings, financial statements and earnings releases with AI-powered insights</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
tab1, tab2 = st.tabs(["📋 Overview & Analysis", "💬 Q&A Chat"])

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

st.info("👈 **Upload a financial document using the sidebar to get started!**")

