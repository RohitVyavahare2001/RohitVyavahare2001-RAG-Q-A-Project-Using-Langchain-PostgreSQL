from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal
from .utils import RAGManager
import os
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()
rag_manager = RAGManager()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ChatRequest(BaseModel):
    question: str
    session_id: str

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Process the PDF
        num_chunks = rag_manager.process_pdf(file_path)
        
        # Clean up the temporary file
        os.remove(file_path)
        
        return {"message": f"PDF processed successfully. Created {num_chunks} chunks."}
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
            
        if not request.session_id.strip():
            raise HTTPException(status_code=400, detail="Session ID cannot be empty")
        
        try:
            response = await rag_manager.generate_response(
                question=request.question,
                session_id=request.session_id,
                db=db
            )
        except TypeError as type_error:
            print(f"TypeError in RAG processing: {str(type_error)}")
            raise HTTPException(
                status_code=500,
                detail="Error processing documents. Please try again."
            )
        except Exception as rag_error:
            print(f"RAG processing error: {str(rag_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating response: {str(rag_error)}"
            )
        
        return response
    
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
) -> List[Dict]:
    try:
        history = (
            db.query(models.ChatHistory)
            .filter(models.ChatHistory.session_id == session_id)
            .order_by(models.ChatHistory.timestamp.desc())
            .all()
        )
        
        return [
            {
                "question": chat.question,
                "answer": chat.answer,
                "timestamp": chat.timestamp
            }
            for chat in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 