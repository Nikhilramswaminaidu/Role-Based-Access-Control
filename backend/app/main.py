# backend/app/main.py

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from .auth import get_current_user, User
from .rag_pipeline import get_rag_response

# Initialize the FastAPI app
app = FastAPI(
    title="FinSolve Internal Chatbot API",
    description="API for the FinSolve role-based access control chatbot.",
    version="1.0.0"
)

# --- Pydantic Models for API ---

# Defines the structure of the chat request body
class ChatRequest(BaseModel):
    query: str
    username: str # We'll get username and password from the request
    password: str

# Defines the structure of the chat response body
class ChatResponse(BaseModel):
    response: str

# --- API Endpoints ---

@app.get("/", tags=["Status"])
async def read_root():
    """A simple endpoint to check if the API is running."""
    return {"status": "FinSolve Chatbot API is running!"}


@app.post("/api/chat", response_model=ChatResponse, tags=["Chatbot"])
async def chat_with_bot(request: ChatRequest):
    """
    Main endpoint for interacting with the chatbot.

    This endpoint requires user credentials in the request body,
    authenticates the user, and then generates a response based on their query
    and role-specific data access.
    """
    # 1. Authenticate the user
    try:
        # Create a mock UserLogin object for the dependency
        from .auth import UserLogin
        user_login_data = UserLogin(username=request.username, password=request.password)
        
        # Manually call the dependency logic
        current_user = await get_current_user(user_login_data)
    except HTTPException as e:
        # Re-raise the authentication exception
        raise e

    # 2. Get the RAG response based on the user's query and role
    rag_response_text = get_rag_response(query=request.query, user_role=current_user.role)

    # 3. Return the response
    return ChatResponse(response=rag_response_text)
