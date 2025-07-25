import streamlit as st

# Page config
st.set_page_config(
    page_title="Q&A Chat",
    page_icon="💬",
    layout="wide"
)

# Title
st.title("💬 Financial Document Q&A")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your document..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        # Simple mock response (replace with your backend call)
        response = f"You asked: '{prompt}'. This is a sample response about your financial document."
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with options
with st.sidebar:
    st.markdown("### Chat Options")
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("🔙 Back to Main"):
        st.switch_page("app.py")
    
    st.markdown("---")
    st.info("💡 Try asking questions about revenue, profits, risks, or key metrics!")