# Document Q&A System

A sophisticated document question-answering system built with FastAPI, Streamlit, and Groq LLM. This system allows users to upload PDF documents and engage in interactive Q&A sessions based on the document's content using RAG (Retrieval-Augmented Generation) technology.

## Features

### Core Functionality
- 📄 PDF Document Processing
- 💬 Interactive Chat Interface
- 🔍 Intelligent Document Retrieval
- 📝 Chat History Tracking
- 🔄 Session Management
- 📊 Vector Store for Efficient Document Search

### Technical Features
- RAG (Retrieval-Augmented Generation) Implementation
- Cosine Similarity for Document Relevance
- PostgreSQL Database Integration
- Asynchronous API Handling
- Vector Embeddings using HuggingFace
- In-memory Vector Store using Qdrant

## Technology Stack

### Backend
- FastAPI - Modern web framework for building APIs
- Langchain - Framework for LLM applications
- Groq - LLM provider for text generation
- PostgreSQL - Database for chat history storage
- Qdrant - Vector database for document storage
- HuggingFace - For text embeddings

### Frontend
- Streamlit - Interactive web interface
- Chat-style UI with message bubbles
- Real-time response display
- Document upload functionality

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip (Python package manager)
- Virtual environment (recommended)

### Running the Application

1. Start the FastAPI backend:
```bash
uvicorn app1.main:app --reload
```

2. Start the Streamlit frontend (in a new terminal):
```bash
streamlit run app1/app.py
```

3. Access the application:
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## Usage Guide

1. **Document Upload**
   - Use the sidebar to upload PDF documents
   - Click "Process Document" to analyze and store the content
   - Wait for confirmation of successful processing

2. **Asking Questions**
   - Type your question in the chat input
   - Press Enter or click Send
   - View the AI's response in the chat interface

3. **Chat History**
   - View current session chat in real-time
   - Click "Show Full Chat History" to see all previous conversations
   - Each conversation is tied to a unique session ID

## Project Structure

```
document-qa-system/
├── app1/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── app.py           # Streamlit interface
│   ├── utils.py         # RAG implementation
│   ├── models.py        # Database models
│   └── database.py      # Database configuration
├── requirements.txt
├── README.md
└── .env
```

## API Endpoints

- `POST /upload-pdf/`: Upload and process PDF documents
- `POST /chat/`: Send questions and receive answers
- `GET /chat-history/{session_id}`: Retrieve chat history

## Error Handling

The system includes comprehensive error handling for:
- Document processing failures
- API connection issues
- Database errors
- Invalid user inputs
- LLM response failures

## Performance Considerations

- Uses chunking for efficient document processing
- Implements vector similarity search for relevant context retrieval
- Maintains session state for continuous conversations
- Optimizes database queries for chat history retrieval

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

Project is licensed under the MIT License. See the LICENSE file for details.
## Acknowledgments

- Groq LLM for text generation
- Langchain for RAG implementation
- FastAPI and Streamlit communities
- HuggingFace for embeddings model
