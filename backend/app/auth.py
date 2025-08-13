# backend/app/auth.py

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict

# --- Mock User Database with Passwords ---
# In a real application, you would NEVER store plain text passwords.
# You would store securely hashed passwords using a library like passlib.
# For this project, we'll use plain text for simplicity.
MOCK_USERS: Dict[str, Dict[str, str]] = {
    "tony_s": {"role": "c_level", "password": "password123"},
    "peter_p": {"role": "engineering", "password": "password123"},
    "susan_m": {"role": "marketing", "password": "password123"},
    "john_f": {"role": "finance", "password": "password123"},
    "lisa_h": {"role": "hr", "password": "password123"},
    "employee_user": {"role": "employee", "password": "password123"},
}

# --- Pydantic Models ---

# Defines the structure for user login data (sent from the frontend)
class UserLogin(BaseModel):
    username: str
    password: str

# Defines the structure of a User object (used internally)
class User(BaseModel):
    username: str
    role: str

# --- FastAPI Dependency for Authentication ---
# This function will now validate a username and password from the request body.
async def get_current_user(form_data: UserLogin = Depends()) -> User:
    """
    Simulates user authentication by checking a username and password.

    This dependency takes the user's login details from the request body,
    validates them against the mock database, and returns the user's info.

    Args:
        form_data (UserLogin): The user's login credentials (username and password).

    Raises:
        HTTPException: If the user is not found or the password is incorrect.

    Returns:
        User: A User object containing the username and their assigned role.
    """
    user_in_db = MOCK_USERS.get(form_data.username)
    
    # Check if user exists and if the password is correct
    if not user_in_db or user_in_db.get("password") != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(username=form_data.username, role=user_in_db["role"])

# --- Example of how to use this dependency in another file (e.g., main.py) ---
#
# from fastapi import FastAPI, Depends
# from .auth import get_current_user, User
#
# app = FastAPI()
#
# # Note: The dependency is now used in the endpoint that requires authentication.
# # The login logic itself would be on a separate /login endpoint.
# # For this project, we can simplify and have the chat endpoint handle it.
#
# @app.post("/chat")
# async def chat_endpoint(current_user: User = Depends(get_current_user)):
#     # This endpoint is now protected. It will only run if get_current_user
#     # successfully validates the username and password from the request body.
#     return {"message": f"Hello {current_user.username}! Your role is {current_user.role}."}
#
