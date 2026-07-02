from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(
    title="Product Review AI", 
    description="API for sentiment analysis, fake review detection, and LLM insights",
    version="1.0.0")

app.include_router(router)

@app.get("/")
def root():
    return {"status": "running", "message": "Welcome to Product Review AI API!"}