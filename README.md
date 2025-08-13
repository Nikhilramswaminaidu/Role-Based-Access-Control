FinSolve Internal Chatbot with Role-Based Access Control (RBAC)

This project is an advanced internal chatbot developed for FinSolve Technologies, a leading FinTech company. The chatbot is designed to address communication delays and data access barriers by providing a secure, AI-powered interface for employees to query company documents. It features a robust Role-Based Access Control (RBAC) system, ensuring that users can only access information appropriate for their specific role.

Key Features

Role-Based Access Control (RBAC): A secure system that restricts data access based on user roles (e.g., Finance, Marketing, HR, C-Level, Employee).

Retrieval-Augmented Generation (RAG): The chatbot uses a RAG pipeline to retrieve relevant information from a vector database and generate accurate, context-aware answers, preventing the AI from making up information.

Interactive Chat Interface: A user-friendly web interface built with Streamlit that includes user authentication and a real-time conversational experience.

Modular Backend: A scalable and robust backend built with FastAPI, separating concerns like authentication, the RAG pipeline, and API logic.

Efficient Data Ingestion: A script that automatically processes various document types (.pdf, .md, .csv), assigns role-based metadata, and stores them as vector embeddings in a ChromaDB database.

System Architecture

The project follows a modern, decoupled architecture with a clear separation between the frontend and backend.

Frontend (Streamlit): The user interacts with a web application built with Streamlit. It handles user login and sends chat queries to the backend.

Backend (FastAPI): A FastAPI server receives the requests. It first authenticates the user and identifies their role.

RAG Pipeline: The backend uses the user's role to query a ChromaDB vector store, retrieving only the documents the user is permitted to see.

LLM (Google Gemini): The retrieved documents are passed to the Google Gemini model, which generates a final, accurate response.

Vector Database (ChromaDB): Stores the vectorized content of all company documents, with metadata for each chunk indicating its source and associated role.

Tech Stack

Component: Frontend
Technology: Streamlit

Component: Backend
Technology: FastAPI, Uvicorn

Component: AI / LLM
Technology: Google Gemini, LangChain

Component: Vector DB
Technology: ChromaDB

Component: Embeddings
Technology: Hugging Face all-MiniLM-L6-v2

Component: Core Language
Technology: Python 3.11+

Project Structure

finsolve_chatbot/
├── backend/
│   ├── app/
│   │   ├── init.py
│   │   ├── main.py             # FastAPI app definition, endpoints
│   │   ├── auth.py             # User authentication and role management
│   │   ├── rag_pipeline.py     # Core RAG logic
│   │   └── data_loader.py      # Script for data ingestion
│   └── .env                    # API keys and secrets
│
├── frontend/
│   └── app.py                  # Streamlit UI for the chatbot
│
├── data/
│   ├── finance/
│   ├── marketing/
│   ├── hr/
│   ├── engineering/
│   └── general/
│
├── chroma_db/                  # Persisted vector database
│
├── requirements.txt            # List of all Python dependencies
└── README.md                   # Project documentation

Getting Started

Follow these steps to set up and run the project locally.

Prerequisites

Python 3.11 or later
Git

Clone the Repository

git clone https://github.com/YourUsername/YourRepositoryName.git
cd YourRepositoryName

Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

Create the virtual environment
python -m venv .venv

Activate it
On Windows:
..venv\Scripts\activate

On macOS/Linux:
source .venv/bin/activate

Install Dependencies

pip install -r requirements.txt

Configure Environment Variables

Navigate to the backend directory.

Create a file named .env.

Add your Google Gemini API key to the file:
GOOGLE_API_KEY="your-google-api-key-here"

Ingest the Data

Before running the chatbot, you need to process your documents and load them into the vector database.

Run this command from the project's root directory
python backend/app/data_loader.py

This script will read all files from the data/ subdirectories, create vector embeddings, and save them to the chroma_db folder.

Running the Application

You need to run the backend and frontend servers in two separate terminals.

Terminal 1: Start the Backend (FastAPI)

Navigate to the backend directory
cd backend

Start the server
uvicorn app.main:app --reload

The API will be running at http://127.0.0.1:8000.

Terminal 2: Start the Frontend (Streamlit)

Navigate to the project's root directory
(Make sure you are not in the backend folder)
Run the Streamlit app
streamlit run frontend/app.py

This will automatically open the chatbot interface in your web browser.

Roles and Permissions

The chatbot enforces strict access control based on the logged-in user's role.

Role: C-Level
Username: tony_s
Password: password123
Accessible Data: Full access to all company data.

Role: Finance
Username: john_f
Password: password123
Accessible Data: Financial reports, expenses, and general info.

Role: Marketing
Username: susan_m
Password: password123
Accessible Data: Campaign data, customer feedback, and general info.

Role: HR
Username: lisa_h
Password: password123
Accessible Data: Employee data, payroll, performance, and general info.

Role: Engineering
Username: peter_p
Password: password123
Accessible Data: Technical architecture, processes, and general info.

Role: Employee
Username: employee_user
Password: password123
Accessible Data: General company policies, events, and FAQs only.

Future Improvements

Token-Based Authentication: Implement a more secure authentication system using JWT tokens instead of sending passwords with each request.

Advanced Retrieval: Integrate more sophisticated retrieval strategies like multi-query retriever or contextual compression to improve accuracy.

Conversation History: Enable the chatbot to remember the context of the current conversation for follow-up questions.

Streaming Responses: Implement response streaming to display the chatbot's answer word-by-word for a better user experience.

Dockerize Application: Containerize the frontend and backend services for easier deployment and scalability.

This project was developed as a solution to the FinTech internal chatbot challenge. For any questions, please feel free to reach out.
