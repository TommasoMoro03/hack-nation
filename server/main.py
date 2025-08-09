from fastapi import FastAPI
from api.v1 import api_router

app = FastAPI(
    title="My Web App API",
    description="API backend per la mia web app",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Backend running"}