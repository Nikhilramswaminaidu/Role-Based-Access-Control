import os
import pathlib
import shutil
from dotenv import load_dotenv

# --- NEW: Import the core chromadb client ---
import chromadb

# ChromaDB - Vector Database
from langchain_community.vectorstores import Chroma

# Document Loaders
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
)

# Text Splitters
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

# Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# --- CONFIGURATION ---
load_dotenv()

# --- PATHS CONFIGURATION ---
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data"
CHROMA_PERSIST_DIRECTORY = PROJECT_ROOT / "chroma_db"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_COLLECTION_NAME = "finsolve_chatbot"


def get_documents_from_path(data_path):
    """
    Loads all documents from the specified path and assigns metadata.
    """
    all_docs = []
    for dirpath, dirnames, filenames in os.walk(data_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            loader = None
            docs = None  # <-- Ensure docs is always defined

            # --- NEW: Use MarkdownHeaderTextSplitter for .md files ---
            if filename.endswith(".md"):
                # For markdown, we read the file content directly
                with open(file_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                
                headers_to_split_on = [
                    ("#", "Header 1"),
                    ("##", "Header 2"),
                    ("###", "Header 3"),
                ]
                
                markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
                docs = markdown_splitter.split_text(markdown_content)
                
                # Manually add source metadata since the splitter doesn't do it automatically
                for doc in docs:
                    doc.metadata["source"] = filename
            
            else: # Use standard loaders for other file types
                if filename.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                elif filename.endswith(".csv"):
                    loader = CSVLoader(file_path)
                
                if loader:
                    docs = loader.load()

            if docs:  # <-- Now you can safely check docs
                role = pathlib.Path(dirpath).name
                for doc in docs:
                    # Ensure role is added to all documents
                    doc.metadata['role'] = role
                all_docs.extend(docs)
                print(f"Loaded and processed {filename} with role '{role}'")

    return all_docs


def ingest_data():
    """
    Main function to ingest data into the ChromaDB vector store.
    """
    print("Starting data ingestion process...")

    if os.path.exists(CHROMA_PERSIST_DIRECTORY):
        print(f"Removing existing ChromaDB directory: {CHROMA_PERSIST_DIRECTORY}")
        shutil.rmtree(CHROMA_PERSIST_DIRECTORY)

    documents = get_documents_from_path(DATA_PATH)
    if not documents:
        print("No documents found. Aborting.")
        return

    # The Markdown splitter has already chunked the .md files.
    # We only need to split the other documents.
    # For simplicity in this project, we'll re-split all, but in a larger system,
    # you might separate the logic.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunked_docs = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunked_docs)} chunks.")

    print(f"Initializing embedding model: {EMBEDDING_MODEL_NAME}")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    print("Connecting to ChromaDB and uploading documents...")
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIRECTORY))
    
    Chroma.from_documents(
        documents=chunked_docs,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=str(CHROMA_PERSIST_DIRECTORY),
        client=client,
    )

    print("---" * 20)
    print("✅ Data ingestion complete!")
    print(f"Total chunks processed: {len(chunked_docs)}")
    print(f"Collection '{CHROMA_COLLECTION_NAME}' is ready in ChromaDB at '{CHROMA_PERSIST_DIRECTORY}'")
    print("---" * 20)


if __name__ == "__main__":
    ingest_data()
