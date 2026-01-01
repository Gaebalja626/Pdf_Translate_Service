import os
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
sys.path.append(os.path.dirname(__file__))

from config import UPLOAD_DIR, RESULT_DIR, MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS
from services.ocr_service import OCRService
from services.translation_service import TranslationService
from services.pdf_generator import PDFGenerator

# Initialize FastAPI app
app = FastAPI(title="OCR Translation Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Initialize services (lazy loading)
ocr_service: Optional[OCRService] = None
translation_service: Optional[TranslationService] = None
pdf_generator: Optional[PDFGenerator] = None

# Task storage (in-memory, use Redis for production)
tasks = {}


def get_ocr_service():
    """Lazy load OCR service"""
    global ocr_service
    if ocr_service is None:
        ocr_service = OCRService()
    return ocr_service


def get_translation_service():
    """Lazy load translation service"""
    global translation_service
    if translation_service is None:
        translation_service = TranslationService()
    return translation_service


def get_pdf_generator():
    """Lazy load PDF generator"""
    global pdf_generator
    if pdf_generator is None:
        pdf_generator = PDFGenerator()
    return pdf_generator


@app.get("/")
async def root():
    """Serve frontend"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "OCR Translation Service API"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload PDF file for processing
    
    Returns task_id for tracking progress
    """
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_UPLOAD_SIZE // 1024 // 1024}MB)")
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_path = UPLOAD_DIR / f"{task_id}.pdf"
    with open(upload_path, "wb") as f:
        f.write(content)
    
    # Create task
    tasks[task_id] = {
        "status": "uploaded",
        "progress": 0,
        "message": "File uploaded successfully",
        "created_at": datetime.now().isoformat(),
        "filename": file.filename
    }
    
    # Start processing in background
    asyncio.create_task(process_pdf(task_id, str(upload_path)))
    
    return {
        "task_id": task_id,
        "message": "File uploaded successfully, processing started"
    }


@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """Get processing status"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]


@app.get("/api/download/{task_id}")
async def download_result(task_id: str):
    """Download translated PDF"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Processing not completed yet")
    
    result_path = task.get("result_path")
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    original_filename = task.get("filename", "document.pdf")
    translated_filename = f"translated_{original_filename}"
    
    return FileResponse(
        result_path,
        media_type="application/pdf",
        filename=translated_filename
    )


async def process_pdf(task_id: str, pdf_path: str):
    """Background task to process PDF"""
    try:
        # Update status
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        tasks[task_id]["message"] = "Starting OCR..."
        
        # OCR
        ocr = get_ocr_service()
        pages_data = ocr.process_pdf(pdf_path)
        
        tasks[task_id]["progress"] = 40
        tasks[task_id]["message"] = "OCR completed, starting translation..."
        
        # Translation
        translator = get_translation_service()
        for page_data in pages_data:
            page_data["paragraphs"] = translator.translate_paragraphs(page_data["paragraphs"])
        
        tasks[task_id]["progress"] = 70
        tasks[task_id]["message"] = "Translation completed, generating PDF..."
        
        # Generate PDF
        generator = get_pdf_generator()
        result_path = RESULT_DIR / f"{task_id}_translated.pdf"
        generator.generate_pdf(pages_data, str(result_path))
        
        # Update task
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["message"] = "Processing completed successfully"
        tasks[task_id]["result_path"] = str(result_path)
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"Error: {str(e)}"
        tasks[task_id]["error"] = str(e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
