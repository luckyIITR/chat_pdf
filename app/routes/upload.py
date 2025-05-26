from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_processor import process_pdf

import uuid

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Generate a unique session ID
        session_id = str(uuid.uuid4())

        # Process the uploaded PDF and store vectors
        process_pdf(file, session_id)

        return {"message": "PDF processed successfully.", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")