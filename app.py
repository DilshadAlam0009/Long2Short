from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import shutil
import asyncio

from services.cleanup import cleanup_expired_sessions
from services.rag import ask_question
from schemas.schema import ChatRequest
from services.pdf import load_pdf
from services.chunking import split_documents
from services.chroma import add_documents
from services.session import create_session
from config import settings

from contextlib import asynccontextmanager
import asyncio

UPLOAD_DIR = Path(settings.UPLOAD_PATH)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def cleanup_loop():

    while True:

        await asyncio.sleep(60)

        cleanup_expired_sessions()


from contextlib import asynccontextmanager
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):

    cleanup_task = asyncio.create_task(cleanup_loop())

    yield
    cleanup_task.cancel()


app = FastAPI(lifespan=lifespan)


@app.post("/rag/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # 1. Check file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

   
    session_id = str(uuid.uuid4())

    
    pdf_path = UPLOAD_DIR / f"{session_id}.pdf"

    
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        
        create_session(session_id)

       
        documents = load_pdf(str(pdf_path))

        
        chunks = split_documents(documents)

        
        add_documents(
            chunks,
            session_id
        )

       

        return {
            "message": "PDF uploaded successfully",
            "session_id": session_id,
            "pages": len(documents),
            "chunks": len(chunks)
        }

    except Exception as e:

        
        if pdf_path.exists():
            pdf_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}"
        )





@app.post("/rag/chat")
async def chat(request: ChatRequest):

    try:

        answer = ask_question(
            question=request.question,
            session_id=request.session_id
        )

        if answer is None:
            return {
                "session_expired": True,
                "message": "Your chat session has expired. Please upload your PDF again."
            }

        return {
            "session_id": request.session_id,
            "question": request.question,
            "answer": answer
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


