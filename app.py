import streamlit as st
from datetime import datetime
from backend.model_pdfplumber import build_index_from_pdf
from backend.model_docling import build_index_from_pdf_docling
from backend.utils import extract_key_metrics, extract_risk_factors
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
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'key_metrics' not in st.session_state:
    st.session_state.key_metrics = None
if 'risk_factors' not in st.session_state:
    st.session_state.risk_factors = None


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
            st.session_state.risk_factors = extract_risk_factors(st.session_state.index)
            st.success("✅ Document processed for Q&A!")
            
    

# Main content

# Welcome screen
st.markdown('<h1 class="main-title">📊 Financial Statement Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyze 10-K filings, financial statements and earnings releases with AI-powered insights</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

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
    st.markdown("---")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("### **Company Name**")
        st.markdown(f"<h4 style='color:#4CAF50;'>{metrics.get('company_name', 'N/A')}</h4>", unsafe_allow_html=True)

    with col5:
        st.markdown("### **Fiscal Year**")
        st.markdown(f"<h4 style='color:#4CAF50;'>{metrics.get('fiscal_year', 'N/A')}</h4>", unsafe_allow_html=True)

    with col6:
        st.markdown("### **Total Assets ($ million)**")
        assets_value = metrics.get('assets')
        if assets_value is not None:
            st.markdown(f"<h4 style='color:#4CAF50;'>{assets_value:,.0f}</h4>", unsafe_allow_html=True)
        else:
            st.markdown("<h4 style='color:#4CAF50;'>N/A</h4>", unsafe_allow_html=True)

    # ------ Financial Metrics Display ------
    st.markdown("---")
    st.markdown("#### 📊 Key Financial Metrics")

    col7, col8, col9, col10 = st.columns(4)

    # Extract metrics
    revenue = metrics.get('revenue', {})
    net_profit = metrics.get('net_profit', {})
    profit_margin = metrics.get('profit_margin', {})
    eps = metrics.get('eps', {})

    def has_valid_metric(metric_dict):
        return (
            isinstance(metric_dict, dict) 
            and isinstance(metric_dict.get("current"), (int, float))
        )
    
    show_metrics = any([
        has_valid_metric(revenue),
        has_valid_metric(net_profit),
        has_valid_metric(profit_margin),
        has_valid_metric(eps)
    ])
    
    if show_metrics:
        with col7:
            value, delta = "N/A", None
            if isinstance(revenue, dict):
                current_revenue = revenue.get('current')
                previous_revenue = revenue.get('previous')
                if current_revenue is not None and previous_revenue is not None:
                    change_revenue = (current_revenue-previous_revenue) / previous_revenue * 100
                    value = f"${current_revenue:,.0f}"
                    delta = f"{change_revenue:.2f}%" 
                
            st.metric(
                label="💵 Revenue ($ million)",
                value=value,
                delta=delta
            )


        with col8:
            # Default values
            value, delta = "N/A", None
            if isinstance(net_profit, dict):
                current_profit = net_profit.get('current')
                previous_profit = net_profit.get('previous')
                if current_profit is not None and previous_profit is not None:
                    change_profit = (current_profit-previous_profit) / previous_profit * 100
                    value = f"${current_profit:,.0f}" 
                    delta = f"{change_profit:.2f}%"             
                
            st.metric(
                label="💹 Net Profit ($ million)",
                value=value,
                delta=delta
            )


        with col9:
            value, delta = "N/A", None
            if isinstance(profit_margin, dict):
                current_margin = profit_margin.get('current')
                previous_margin = profit_margin.get('previous')
                if current_margin is not None and previous_margin is not None:
                    change_margin = (current_margin-previous_margin) / previous_margin * 100
                    value = f"{current_margin:.1f}%" 
                    delta = f"{change_margin:.2f}%" 

            st.metric(
                label="📈 Profit Margin",
                value=value,
                delta=delta
            )

        with col10:
            value, delta = "N/A", None
            if isinstance(eps, dict):
                current_eps = eps.get('current')
                previous_eps = eps.get('previous')
                if current_eps is not None and previous_eps is not None:
                    change_eps = (current_eps-previous_eps) / previous_eps * 100
                    value = f"${current_eps:.2f}"
                    delta = f"{change_eps:.2f}%" 

            st.metric(
                label="📊 EPS",
                value=value,
                delta=delta
            )
    else:
        st.markdown("📉 No financial metrics available for display.")

    # ------ Risk Factors Display ------
    st.markdown("---")
    st.markdown("#### ⚠️ Major Risk Factors and Business Highlights")
    if st.session_state.risk_factors:
        risk_factors = st.session_state.risk_factors.replace("$", r"\$")
        if risk_factors:
            st.markdown(f"""
                <div class="analysis-card">   
                    <strong>Status:</strong>
                <span style = "color: #475569">⚠️{risk_factors}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""<div class="analysis-card">
            <strong>Status:</strong>
            <span style = "color: #475569">✅ No major risk factors identified</span>
        </div>
        """, unsafe_allow_html=True)
