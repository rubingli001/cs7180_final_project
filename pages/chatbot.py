import streamlit as st
from backend.model_docling import create_role_prompts, query_index_with_roles, query_index
from openai import OpenAI
from dotenv import load_dotenv
import os
from streamlit_mic_recorder import mic_recorder

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI API for audio input
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(
    page_title="Q&A Chat",
    page_icon="💬",
    layout="wide"
)

# Role-based configuration for the user
ROLE_OPTIONS  = {
    "🎓 Beginner": {
        "icon": "🎓",
        "description": "I have limited background knowledge in finance and accounting.",
        "sample_questions" : [
            "What does the company do?",
            "How much profit did the company make last year?"
        ]
    },
    "📊 Financial Analyst": {
        "icon": "📊",
        "description": "I have a solid understanding of financial concepts, metrics and ratios.",
        "sample_questions": [
            "What are the key financial ratios?",
            "Compare ROIC vs WACC over the reporting periods."
        ]
    },
    "💼 Investor": {
         "icon": "💼",
        "description": "I am looking for investment-focused insights and portfolio decisions",
        "sample_questions": [
            "Is the stock worth buying?",
            "What are the risks associated with this investment?"
        ]
    }
}
# Title
st.title("💬 Financial Document Q&A")

# Voice mode toggle
voice_mode = st.toggle("🎤 Speak My Question")

# Initialize the session state for chat messages, document index embedded and user role
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", 
         "content": "👋 Hi! I'm your financial document assistant. Feel free to ask questions!"}
    ]

if "index" not in st.session_state:
    st.warning("⚠️ Please note that no document has been uploaded yet. ")
    st.session_state.index = None

if "role" not in st.session_state:
    st.session_state.role = "🎓 Beginner"

if "use_openAI" not in st.session_state:
    st.session_state.use_openAI = False

# --- Voice Input Section ---
voice_input = None
if voice_mode:
    st.markdown("Click the button below to start recording your question.")
    audio = mic_recorder(
            start_prompt="🎙 Start Recording", 
            stop_prompt="⏹ Stop Recording",
            just_once=True,
            use_container_width=True
        )
    if audio:
        st.audio(audio['bytes'])
        with open("temp_voice.wav", "wb") as f:
            f.write(audio['bytes'])

        # Transcribe with Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=open("temp_voice.wav", "rb")
        )
        voice_input = transcript.text
        st.success(f"🗣 You said: {voice_input}")


# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Text Input Section ---

text_input = st.chat_input("Ask a question about your document...")

# Combine input sources
user_input = voice_input if voice_input else text_input

# Chat input
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant response
    response = ""
    with st.chat_message("assistant"):
        # Simple mock response (replace with your backend call)
        if st.session_state.index:
            with st.spinner("💡 Thinking..."):
                response = query_index_with_roles(
                    st.session_state.index, 
                    user_input, 
                    st.session_state.role,
                    st.session_state.use_openAI
                )

            response = response.replace("$", r"\$")  # Escape dollar signs so that Streamlit won't interpret them as LaTeX
            st.markdown(response)
        else:
            response = "Please upload a document first so that I can help. 😊"
            st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with options
with st.sidebar:

    st.info("💡 Try asking questions about revenue, profits, risks, or key metrics!")
 
    # Role selection
    st.markdown("### Select Your Role")
    selected_role = st.selectbox(
        "Choose your role:", 
        options=list(ROLE_OPTIONS.keys())
    )

    if selected_role != st.session_state.role:
        st.session_state.role = selected_role

    st.markdown(f"{ROLE_OPTIONS[selected_role]['icon']} {ROLE_OPTIONS[selected_role]['description']}")
    st.markdown("#### Sample Questions:")
    for question in ROLE_OPTIONS[selected_role]["sample_questions"]:
        st.markdown(f"- {question}")

    st.markdown("---")

    st.markdown("### Chat Options")

    use_openAI = st.toggle(
        "Switch AI model for longer responses", 
        value=st.session_state.use_openAI
    )

    if use_openAI != st.session_state.use_openAI:
        st.session_state.use_openAI = use_openAI

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [
        {"role": "assistant", 
         "content": "👋 Hi! I'm your financial document assistant. Feel free to ask questions!"}
    ]
        st.rerun()
    
    if st.button("🔙 Back to Main"):
        st.switch_page("app.py")
    