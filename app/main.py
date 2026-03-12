from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.webhook import router as webhook_router

app = FastAPI()

app.include_router(webhook_router)

@app.get("/")
def root():
    return {"message": "GitHub AI Bot is running"}