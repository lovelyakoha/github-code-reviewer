from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.webhook import router as webhook_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(webhook_router)

@app.get("/")
def root():
    return FileResponse("static/index.html")