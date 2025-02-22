import streamlit as st
import requests
import uuid
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

# API endpoint
API_URL = "http://localhost:8000"

def send_message(question: str, session_id: str) -> Dict:
    if not question.strip():
        st.error("Please enter a question")
        return None
        
    try:
        response = requests.post(
            f"{API_URL}/chat/",
            json={"question": question, "session_id": session_id},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and "answer" in result:
                return result
            else:
                st.error("Invalid response format from API")
                return None
        else:
            error_detail = response.json().get('detail', response.text)
            st.error(f"API Error: {error_detail}")
            return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Please ensure the server is running.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Document Q&A System", layout="wide")
    st.title("Document Q&A System")
    
    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None:
            if st.button("Process Document"):
                with st.spinner("Processing document..."):
                    try:
                        files = {"file": uploaded_file}
                        response = requests.post(f"{API_URL}/upload-pdf/", files=files)
                        if response.status_code == 200:
                            st.success("Document uploaded and processed successfully!")
                            st.session_state.document_uploaded = True
                        else:
                            st.error(f"Error processing document: {response.text}")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")

    # Main chat interface
    st.header("Chat with your Document")
    
    # Show warning if no document is uploaded
    if not getattr(st.session_state, 'document_uploaded', False):
        st.warning("Please upload a PDF document first using the sidebar.")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your document"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get AI response
        with st.spinner("Thinking..."):
            response = send_message(prompt, st.session_state.session_id)
            if response and "answer" in response:
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
                with st.chat_message("assistant"):
                    st.write(response["answer"])
    
    # Chat history button
    if st.button("Show Full Chat History", key="show_history"):
        try:
            response = requests.get(f"{API_URL}/chat-history/{st.session_state.session_id}")
            if response.status_code == 200:
                history = response.json()
                st.subheader("Full Chat History")
                for entry in history:
                    with st.chat_message("user"):
                        st.write(entry["question"])
                    with st.chat_message("assistant"):
                        st.write(entry["answer"])
            else:
                st.error(f"Error fetching chat history: {response.text}")
        except Exception as e:
            st.error(f"Error fetching chat history: {str(e)}")

    # Debug information
    with st.expander("Debug Information"):
        st.write("Session ID:", st.session_state.session_id)
        st.write("API URL:", API_URL)
        st.write("Number of messages:", len(st.session_state.messages))
        st.write("Document uploaded:", getattr(st.session_state, 'document_uploaded', False))

if __name__ == "__main__":
    main() 