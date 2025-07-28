from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.readers.docling import DoclingReader
import os
from docling.datamodel.pipeline_options import PdfPipelineOptions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False  # Skip OCR for text-based PDFs
pipeline_options.do_table_structure = True  # Keep table detection

def build_index_from_pdf_docling(pdf_file):
    # Extract pdf information using Docling)
    reader = DoclingReader()
    documents = reader.load_data(pdf_file)

    # Node parsing (semantic chunking)
    node_parser = MarkdownNodeParser()
    nodes = node_parser.get_nodes_from_documents(documents)
    for i, node in enumerate(nodes):
        print(f"\n--- Node {i+1} ---")
        print(f"Text:\n{node.text[:1000]}")
        print(f"Metadata: {node.metadata}")


    # Indexing
    index = VectorStoreIndex.from_documents(documents, transformations=[node_parser])

    return index
