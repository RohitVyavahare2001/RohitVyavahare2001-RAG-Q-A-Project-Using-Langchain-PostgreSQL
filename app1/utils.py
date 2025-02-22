from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_core.documents import Document
import os
from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from sqlalchemy.orm import Session
from . import models
from dotenv import load_dotenv

load_dotenv()

class RAGManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            if not os.getenv("GROQ_API_KEY"):
                raise ValueError("GROQ_API_KEY environment variable is not set")
            
            self.qdrant_client = QdrantClient(":memory:")
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.llm = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model="qwen-2.5-32b"
            )
            
            try:
                self.qdrant_client.create_collection(
                    collection_name="documents",
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
            except Exception:
                pass
            
            self.vector_store = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name="documents",
                embedding=self.embeddings
            )
            self.initialized = True

    def process_pdf(self, file_path: str) -> int:
        """Process PDF and store chunks in vector store"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            self.vector_store.add_documents(chunks)
            return len(chunks)
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            raise e

    async def generate_response(
        self,
        question: str,
        session_id: str,
        db: Session
    ) -> Dict[str, str]:
        """Generate response using RAG with improved context handling"""
        try:
            recent_history = (
                db.query(models.ChatHistory)
                .filter(models.ChatHistory.session_id == session_id)
                .order_by(models.ChatHistory.timestamp.desc())
                .limit(5)
                .all()
            )
            
            chat_history = "\n".join([
                f"Q: {h.question}\nA: {h.answer}"
                for h in reversed(recent_history)
            ])
            
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 5}
            )
            docs = retriever.get_relevant_documents(question)
            
            scored_docs = self._score_documents(question, docs)
            most_relevant_docs = scored_docs[:3]
            
            doc_context = "\n".join([doc.page_content for doc in most_relevant_docs])
            
            prompt = f"""Based on the following context and chat history, provide a relevant and accurate answer.
            If the answer cannot be found in the context, say so.
            
            Context: {doc_context}
            
            Previous conversation:
            {chat_history}
            
            Question: {question}
            """
            
            response = self.llm.invoke(prompt)
            answer = response.content
            
            chat_entry = models.ChatHistory(
                session_id=session_id,
                question=question,
                answer=answer
            )
            db.add(chat_entry)
            db.commit()
            
            return {
                "answer": answer,
                "session_id": session_id
            }
            
        except Exception as e:
            db.rollback()
            raise e

    def _score_documents(self, question: str, docs: List[Document]) -> List[Document]:
        """Score documents based on relevance to question"""
        try:
            question_embedding = self.embeddings.embed_query(question)
            
            scored_docs = []
            for doc in docs:
                doc_embedding = self.embeddings.embed_query(doc.page_content)
                similarity = self._cosine_similarity(question_embedding, doc_embedding)
                # Store as tuple with unique identifier to avoid comparison issues
                scored_docs.append((similarity, id(doc), doc))
            
            # Sort by similarity score only
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            return [doc for _, _, doc in scored_docs]
        except Exception as e:
            print(f"Error in document scoring: {str(e)}")
            return docs  # Return original docs if scoring fails

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        return dot_product / (norm1 * norm2) 