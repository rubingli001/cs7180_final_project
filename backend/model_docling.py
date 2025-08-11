from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.readers.docling import DoclingReader
from llama_index.llms.openrouter import OpenRouter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding 
from docling.datamodel.pipeline_options import PdfPipelineOptions

from dotenv import load_dotenv
import os
import streamlit as st

# Load environment variables
load_dotenv() 
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")


# Initialize both LLMs
openrouter_llm = OpenRouter(
    model="anthropic/claude-sonnet-4", 
    api_key=os.getenv("OPENROUTER_API_KEY"))
    
openai_llm = OpenAI(
    model="gpt-4o",  # or "gpt-3.5-turbo", "gpt-4-turbo", etc.
    api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=4096   # Optional: control response length
)

# Set default LLM to OpenRouter

llm = openrouter_llm


# Configure OpenAI Large Embedding Model
openai_embedding = OpenAIEmbedding(
    model="text-embedding-3-large",  
    api_key=os.getenv("OPENAI_API_KEY"))

# maximum input size to the LLM
Settings.context_window = 4096
# number of tokens reserved for text generation.
Settings.num_output = 1000
Settings.embed_model = openai_embedding

# ---------- Function to set the LLM based on the user's choice -----

def set_llm(use_openAI=False):
    return openai_llm if use_openAI else openrouter_llm

# ----------------- PDF extraction using Docling ----------------
def build_index_from_pdf_docling(pdf_file):
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False  # Skip OCR for text-based PDFs
    pipeline_options.do_table_structure = True  # Keep table detection

    # Extract pdf information using Docling)
    reader = DoclingReader()
    documents = reader.load_data(pdf_file)

    # Node parsing (semantic chunking)
    print(f"📄 Extracted {len(documents)} documents from {pdf_file}")
    node_parser = MarkdownNodeParser()  # Adjust chunk size and overlap as needed
    nodes = node_parser.get_nodes_from_documents(documents)
    print(f"🔍 Parsed {len(nodes)} nodes from documents.")
    for i, node in enumerate(nodes[:5]):
        if i == 1:  # Show first 5 nodes
            print(f"\n--- Node {i+1} ---")
            print(f"Text length: {len(node.text)} characters")
            print(f"Text preview: {node.text}")
            print("-" * 50)

    # Indexing
    index = VectorStoreIndex.from_documents(documents, transformations=[node_parser])

    return index


def query_index(index: VectorStoreIndex, query: str, llm=llm):

    engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=5,
        response_mode = "tree_summarize"
    )
    response = engine.query(query)
    return str(response)


# ----------------- Querying with role-based context ----------------
# Create role-specific prompts based on user role
def create_role_prompts(user_role):
    role_prompts = {
        "🎓 Beginner": """
        You are responding to some one new to finance. Avoid complex ratios or technical analysis unless specifically requested.
        Limit answers to fewer than 200 words.
        Provide:
        - Simple, clear explanations without jargon
        - Define any financial terms you must use
        - Use analogies and examples to explain concepts
        """,
        "📊 Financial Analyst": """
        You are responding to a professional financial analyst. Summarize in professional tone. Provide:
        - Detailed quantitative analysis with specific ratios and metrics based on the data in the document
        - Technical financial terminology and methodologies
        - The impact on the financial performance and accounting treatment

        """,
        "💼 Investor": """
        You are responding to an investor. Provide:
        - Investment thesis and valuation insights
        - Risk-return analysis and portfolio implications
        - Key catalysts and potential red flags
        """
    }

    return role_prompts.get(user_role, role_prompts["🎓 Beginner"])


def query_index_with_roles(index: VectorStoreIndex, question: str, user_role: str, use_openAI=False):
    try:
        selected_llm = set_llm(use_openAI)
        role_context = create_role_prompts(user_role)

        # Combine role context with user query
        combined_query = f"""
        {role_context}
        User Question: {question}
        """
        # Query the index with the combined query
        print(f"🔍 Querying index with role context: {combined_query}")
        response = query_index(index, combined_query, selected_llm)
        return str(response)
    except Exception as e:
        st.error(f"Error querying index: {str(e)}")
        return "An error occurred while processing your request."


