# backend/app/rag_pipeline.py

import os
import pathlib # Import pathlib
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
# Import the Google Generative AI components
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# Load environment variables from .env file
load_dotenv()

# --- Configuration for Google Gemini ---
# Correctly check for the API key before configuring the library
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    exit()
genai.configure(api_key=google_api_key)


# --- PATHS AND CONSTANTS (FIX) ---
# Get the absolute path to the project's root directory
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent
CHROMA_DB_PATH = PROJECT_ROOT / "chroma_db"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# Use a Gemini model name
LLM_MODEL_NAME = "gemini-1.5-flash"
CHROMA_COLLECTION_NAME = "finsolve_chatbot"


# --- Role-Based Access Control (RBAC) Mapping ---
# Maps user roles to the data roles they are allowed to access.
# This is the core of our RBAC implementation.
ROLE_ACCESS_MAPPING = {
    "c_level": ["c_level", "engineering", "marketing", "finance", "hr", "general"],
    "engineering": ["engineering", "general"],
    "marketing": ["marketing", "general"],
    "finance": ["finance", "general"],
    "hr": ["hr", "general"],
    "employee": ["general"],
}

# --- Initialize Components ---
# Initialize the embedding model
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# --- MORE ROBUST CHROMA INITIALIZATION (FIX) ---
# Initialize the Chroma client first, then get the collection.
# This is a more reliable way to ensure you're connecting to the persisted database.
try:
    chroma_client = Chroma(
        persist_directory=str(CHROMA_DB_PATH),
        embedding_function=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
    )
    # Check if the collection is empty
    if chroma_client._collection.count() == 0:
        print("Warning: ChromaDB collection is empty. Did the data loader run correctly?")
        # You might want to exit or handle this case appropriately
except Exception as e:
    print(f"Error initializing ChromaDB: {e}")
    print("Please ensure the database has been created by running the data_loader.py script.")
    exit()


# Initialize the Language Model with Google Gemini
llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=0.2)

# --- RAG Prompt Template ---
# This template structures the prompt sent to the LLM.
template = """
You are a helpful assistant for FinSolve Technologies.
Answer the question based only on the following context.
If you don't know the answer, just say that you don't know.

Context:
{context}

Question:
{question}
"""
prompt = ChatPromptTemplate.from_template(template)

def get_rag_response(query: str, user_role: str) -> str:
    """
    Generates a response using the RAG pipeline with role-based access control.

    Args:
        query (str): The user's question.
        user_role (str): The role of the user making the query.

    Returns:
        str: The generated response from the LLM.
    """
    # 1. Determine the accessible data roles based on the user's role
    accessible_roles = ROLE_ACCESS_MAPPING.get(user_role, [])
    if not accessible_roles:
        return "Your role does not have access to any data."

    # 2. Configure the retriever with an RBAC filter
    retriever = chroma_client.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5,  # Retrieve top 5 most relevant chunks
            "filter": {"role": {"$in": accessible_roles}}
        }
    )

    # 3. Define the RAG chain using LangChain Expression Language (LCEL)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # 4. Invoke the chain with the user's query
    response = rag_chain.invoke(query)
    
    return response

# --- NEW DEBUGGING FUNCTION ---
def test_retriever(query: str, user_role: str):
    """
    A simple function to test the retriever directly and see what it finds.
    """
    print(f"\n--- Testing Retriever ---")
    print(f"Role: '{user_role}'")
    print(f"Query: '{query}'")
    
    accessible_roles = ROLE_ACCESS_MAPPING.get(user_role, [])
    if not accessible_roles:
        print("Result: No accessible roles found for this user.")
        return

    retriever = chroma_client.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5, "filter": {"role": {"$in": accessible_roles}}}
    )
    
    try:
        relevant_docs = retriever.get_relevant_documents(query)
        print(f"\nFound {len(relevant_docs)} documents:")
        if not relevant_docs:
            print("--> The retriever found NO relevant documents for this query and role.")
            print("--> This is why the chatbot says 'I don't know'.")
            print("--> Check if the data was loaded correctly with the right 'role' metadata.")
        else:
            for i, doc in enumerate(relevant_docs):
                print(f"\n--- Document {i+1} ---")
                print(f"Source: {doc.metadata.get('source', 'N/A')}")
                print(f"Role: {doc.metadata.get('role', 'N/A')}")
                print(f"Content: {doc.page_content[:250]}...") # Print first 250 chars
    except Exception as e:
        print(f"An error occurred during retrieval: {e}")
    print("--- End of Retriever Test ---\n")


if __name__ == '__main__':
    # We will now use the main block to run our debugging function
    test_retriever(query="What is the system architecture?", user_role="engineering")
    test_retriever(query="What were the marketing expenses?", user_role="finance")
    test_retriever(query="What is the policy on remote work?", user_role="employee")
