from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.readers.docling import DoclingReader
from llama_index.llms.openrouter import OpenRouter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv() 
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")


# Initialize OpenRouter LLM
llm = OpenRouter(
    model="anthropic/claude-sonnet-4", 
    pi_key=os.getenv("OPENROUTER_API_KEY"))

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
    node_parser = MarkdownNodeParser()
    nodes = node_parser.get_nodes_from_documents(documents)
    for i, node in enumerate(nodes):
        print(f"\n--- Node {i+1} ---")
        print(f"Text:\n{node.text[:300]}")
        print(f"Metadata: {node.metadata}")


    # Indexing
    index = VectorStoreIndex.from_documents(documents, transformations=[node_parser])

    return index

# ----------------- Querying with role-based context ----------------
# Create role-specific prompts based on user role
def create_role_prompts(user_role):
    role_prompts = {
        "🎓 Beginner": """
        You are responding to some one new to finance. Avoid complex ratios or technical analysis unless specifically requested.
        Provide:
        - Simple, clear explanations without jargon
        - Define any financial terms you must use
        - Use analogies and examples to explain concepts
        """,
        "📊 Financial Analyst": """
        You are responding to a professional financial analyst. Provide:
        - Detailed quantitative analysis with specific ratios and metrics
        - Technical financial terminology and methodologies
        - Professional tone with in-depth explanations
        """,
        "💼 Investor": """
        You are responding to an investor. Provide:
        - Investment thesis and valuation insights
        - Risk-return analysis and portfolio implications
        - Key catalysts and potential red flags
        """
    }

    return role_prompts.get(user_role, role_prompts["🎓 Beginner"])


def query_index_with_roles(index: VectorStoreIndex, question: str, user_role: str):
    try:
        role_context = create_role_prompts(user_role)

        # Combine role context with user query
        combined_query = f"""
        {role_context}
        User Question: {question}
        """
        
        engine = index.as_query_engine(llm=llm)
        response = engine.query(combined_query)
        return str(response)
    except Exception as e:
        st.error(f"Error querying index: {str(e)}")
        return "An error occurred while processing your request."


