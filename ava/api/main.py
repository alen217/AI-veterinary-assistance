from fastapi import FastAPI
from ava.api.skin_disease import router as skin_router

app = FastAPI(title="AI Veterinary Assistance (AVA)")

app.include_router(skin_router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "AVA API running"}
