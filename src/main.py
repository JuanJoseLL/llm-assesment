import os
from typing import Dict
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
import tempfile
import shutil

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from ingestion.pipeline import IngestionPipeline
from retrieval.rag_chain import ConversationalRAGChain

load_dotenv()
app = FastAPI(
    title="RAG API with Conversational Memory",
    description="Question-answering system with multi-turn conversation support",
    version="1.0.0"
)

PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Session management for conversations
conversation_sessions: Dict[str, ConversationalRAGChain] = {}


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """Upload and index a PDF document"""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    try:
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()

        pipeline = IngestionPipeline(api_key=OPENAI_API_KEY)
        chunks = pipeline.process_pdf(temp_file.name)

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY
        )

        Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY,
            collection_name="documents"
        )

        return {"message": "PDF indexed successfully", "chunks": len(chunks)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.unlink(temp_file.name)
        except Exception:
            pass


@app.post("/query")
async def query(
    question: str = Form(...),
    session_id: str = Form(default="default"),
    stream: bool = Form(False)
):
    """
    Query with conversational memory support.

    - question: The user's question
    - session_id: Session ID for conversation tracking (default: "default")
    - stream: Enable streaming response
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    try:
        # Get or create conversation session
        if session_id not in conversation_sessions:
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=OPENAI_API_KEY
            )

            vectorstore = Chroma(
                persist_directory=PERSIST_DIRECTORY,
                collection_name="documents",
                embedding_function=embeddings
            )

            conversation_sessions[session_id] = ConversationalRAGChain(
                vectorstore=vectorstore,
                api_key=OPENAI_API_KEY
            )

        rag = conversation_sessions[session_id]

        if stream:
            async def generate():
                for chunk in rag.stream_query(question):
                    yield chunk
            return StreamingResponse(generate(), media_type="text/plain")
        else:
            result = rag.query_with_sources(question)
            return {
                "answer": result['answer'],
                "sources": result['sources'],
                "session_id": session_id
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{session_id}/history")
async def get_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "history": conversation_sessions[session_id].get_history()
    }


@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session"""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    conversation_sessions[session_id].clear_history()
    del conversation_sessions[session_id]

    return {
        "message": f"Conversation {session_id} cleared successfully"
    }


@app.get("/conversations")
async def list_sessions():
    """List all active conversation sessions"""
    return {
        "active_sessions": list(conversation_sessions.keys()),
        "count": len(conversation_sessions)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
