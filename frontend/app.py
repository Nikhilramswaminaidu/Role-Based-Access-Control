# frontend/app.py

import streamlit as st
import requests
import json

# --- Configuration ---
# Set the title and icon for the browser tab
st.set_page_config(page_title="FinSolve Chatbot", page_icon="🤖")

# API endpoint for the backend
FASTAPI_URL = "http://127.0.0.1:8000/api/chat"

# --- UI Setup ---
st.title("🤖 FinSolve Internal Chatbot")
st.caption("Your AI-powered assistant for secure, role-based data access.")

# Initialize session state variables if they don't exist
# 'messages' will store the chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# 'logged_in' will track the user's authentication status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
# 'username' will store the logged-in user's name
if "username" not in st.session_state:
    st.session_state.username = ""
# 'password' will store the user's password for API requests
if "password" not in st.session_state:
    st.session_state.password = ""

# --- Authentication UI (Sidebar) ---
with st.sidebar:
    st.header("Login")
    # If the user is not logged in, show the login form
    if not st.session_state.logged_in:
        username_input = st.text_input("Username", key="username_input")
        password_input = st.text_input("Password", type="password", key="password_input")
        
        if st.button("Login"):
            if username_input and password_input:
                # For this demo, we'll just store the credentials.
                # The backend will handle the actual validation.
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.session_state.password = password_input
                st.success(f"Logged in as {username_input}")
                # Rerun the script to update the UI
                st.rerun()
            else:
                st.error("Please enter both username and password.")
    
    # If the user is logged in, show their status and a logout button
    if st.session_state.logged_in:
        st.success(f"Logged in as: {st.session_state.username}")
        if st.button("Logout"):
            # Reset all session state variables on logout
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.password = ""
            st.session_state.messages = []
            st.rerun()

# --- Main Chat Interface ---
# Only display the chat interface if the user is logged in
if st.session_state.logged_in:
    # Display previous chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input from the chat box
    if prompt := st.chat_input("Ask me anything about FinSolve..."):
        # Add user's message to the chat history and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare the request to the backend
        payload = {
            "query": prompt,
            "username": st.session_state.username,
            "password": st.session_state.password,
        }

        # Display a thinking indicator while waiting for the response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Send the request to the FastAPI backend
                    response = requests.post(FASTAPI_URL, json=payload)
                    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                    
                    # Get the response text from the API
                    bot_response = response.json().get("response", "Sorry, I encountered an error.")
                
                except requests.exceptions.HTTPError as http_err:
                    # Handle specific HTTP errors (like 401 Unauthorized)
                    if http_err.response is not None and http_err.response.status_code == 401:
                        bot_response = "Authentication failed. Please check your username and password."
                    else:
                        bot_response = f"An HTTP error occurred: {http_err}"
                except requests.exceptions.RequestException as e:
                    # Handle other network-related errors
                    bot_response = f"Failed to connect to the chatbot API. Please ensure the backend is running. Error: {e}"

                # Display the bot's response
                st.markdown(bot_response)

        # Add the bot's response to the chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
else:
    st.info("Please log in using the sidebar to start chatting.")
