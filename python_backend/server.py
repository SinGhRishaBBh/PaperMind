from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from pymongo import MongoClient, errors
from pypdf import PdfReader
from dotenv import load_dotenv
import requests
import tempfile
import os
import logging
import uuid
from contextlib import asynccontextmanager

# ===================== LOAD ENV ===================== #

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000")
OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "PaperMind")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not found")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not found")

# ===================== LOGGING ===================== #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("papermind")

# ===================== DATABASE ===================== #

client: MongoClient | None = None
collection = None

def connect_mongo():
    global client, collection
    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000
        )
        client.admin.command("ping")
        db = client["papermind_db"]
        collection = db["documents"]
        logger.info("MongoDB connected")
    except errors.ServerSelectionTimeoutError:
        raise RuntimeError("MongoDB not reachable")

def close_mongo():
    if client:
        client.close()
        logger.info("MongoDB connection closed")

# ===================== APP LIFESPAN ===================== #

@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_mongo()
    yield
    close_mongo()

app = FastAPI(
    title="PaperMind Backend",
    lifespan=lifespan
)

# ===================== MIDDLEWARE ===================== #

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== REQUEST MODELS ===================== #

class QuestionRequest(BaseModel):
    question: str
    document_id: str

class QuestionResponse(BaseModel):
    answer: str

# ===================== PDF UTILS ===================== #

def extract_text_from_pdf(path: str):
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append((i + 1, text))
    return pages

def chunk_text(text: str, size: int = 900, overlap: int = 300):
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = start + size
        chunks.append(text[start:end])
        start = max(end - overlap, 0)

    return chunks

# ===================== STORAGE ===================== #

def store_chunks(chunks, document_id, source, page):
    docs = [{
        "document_id": document_id,
        "text": chunk,
        "source": source,
        "page": page
    } for chunk in chunks]

    if docs:
        collection.insert_many(docs)

# ===================== CONTEXT RETRIEVAL ===================== #

def retrieve_context(document_id: str, k: int = 10):
    docs = collection.find(
        {"document_id": document_id}
    ).limit(k)

    texts = [doc["text"] for doc in docs]

    return "\n---\n".join(texts)

# ===================== OPENROUTER CALL ===================== #

def call_openrouter(context: str, question: str) -> str:
    prompt = f"""
You are an expert document analyst.

TASK:
Answer the question using ONLY the document content below.

RULES:
- Provide a complete, well-structured answer.
- Do NOT cut sentences.
- Do NOT mention context, AI, model, or prompts.
- If the answer is not present, clearly say it is not found.

DOCUMENT:
{context}

QUESTION:
{question}

FINAL ANSWER:
""".strip()

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": OPENROUTER_SITE_URL,
                "X-Title": OPENROUTER_SITE_NAME
            },
            json={
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1200,
                "temperature": 0.15
            },
            timeout=90
        )

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except requests.RequestException:
        logger.exception("OpenRouter API error")
        raise HTTPException(502, "LLM service unavailable")

# ===================== ASK ENDPOINT ===================== #

@app.post("/ask", response_model=QuestionResponse)
async def ask(request: QuestionRequest):
    context = retrieve_context(request.document_id)

    if not context:
        return QuestionResponse(
            answer="No relevant content found in this document."
        )

    answer = call_openrouter(
        context=context,
        question=request.question
    )

    return QuestionResponse(answer=answer)

# ===================== PDF UPLOAD ===================== #

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")

    document_id = str(uuid.uuid4())

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        pages = extract_text_from_pdf(tmp_path)

        for page_num, text in pages:
            chunks = chunk_text(text)
            store_chunks(chunks, document_id, file.filename, page_num)

        return {
            "message": "PDF ingested successfully",
            "document_id": document_id,
            "pages": len(pages)
        }

    finally:
        os.remove(tmp_path)

# ===================== HEALTH ===================== #

@app.get("/health")
async def health():
    return {"status": "ok"}

# ===================== FAVICON ===================== #

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

# ===================== RUN ===================== #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
