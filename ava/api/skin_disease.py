from fastapi import APIRouter, UploadFile, File
import shutil
import os
import uuid

from ava.skin_disease.predictor import predict_skin_disease

router = APIRouter()

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)


@router.post("/predict/skin-disease")
async def predict_skin_disease_api(file: UploadFile = File(...)):
    # Save uploaded image temporarily
    ext = file.filename.split(".")[-1]
    temp_name = f"{uuid.uuid4()}.{ext}"
    temp_path = os.path.join(TEMP_DIR, temp_name)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run inference
    result = predict_skin_disease(temp_path)

    # Cleanup
    os.remove(temp_path)

    return result
