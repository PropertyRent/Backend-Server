import uuid
from fastapi import UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.file_model import FileModel  # your DB model

# -----------------------------
# Helper function to save file in PostgreSQL
# -----------------------------
async def save_file_to_db(file: UploadFile, db: Session):
    try:
        contents = await file.read()  # read file as bytes
        file_ext = file.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{file_ext}"

        db_file = FileModel(
            file_name=unique_name,
            content=contents,
            content_type=file.content_type,
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file.id  # or return the DB object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

# -----------------------------
# Dependency for single file
# -----------------------------
async def single_file_upload(field_name: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_id = await save_file_to_db(file, db)
    return {"file_id": file_id, "file_name": file.filename, "content_type": file.content_type}

# -----------------------------
# Dependency for multiple files
# -----------------------------
async def multiple_file_upload(field_name: str, files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    file_ids = []
    for file in files:
        file_id = await save_file_to_db(file, db)
        file_ids.append(file_id)
    return {"file_ids": file_ids}
