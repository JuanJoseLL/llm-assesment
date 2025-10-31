import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
import tempfile
import shutil

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from ingestion.pipeline import IngestionPipeline
from retrieval.rag_chain import RAGChain


app = FastAPI(title="RAG API", version="1.0.0")

PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


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
async def query(question: str = Form(...), stream: bool = Form(False)):
    """Query the indexed documents"""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY
        )

        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            collection_name="documents",
            embedding_function=embeddings
        )

        rag = RAGChain(vectorstore=vectorstore, api_key=OPENAI_API_KEY)

        if stream:
            async def generate():
                for chunk in rag.stream_query(question):
                    yield chunk
            return StreamingResponse(generate(), media_type="text/plain")
        else:
            result = rag.query_with_sources(question)
            return {"answer": result['answer'], "sources": result['sources']}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
