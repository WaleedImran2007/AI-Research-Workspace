print("🔥 APP.PY STARTING")

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers.authRouter import router as auth_router
from routers.collectionRouter import router as collection_router
from routers.documentRouter import router as document_router
from routers.chatRouter import router as chat_router
from routers.conversationRouter import router as conversation_router

import os

app = FastAPI()

os.makedirs("generated", exist_ok=True)

app.mount(
    "/generated",
    StaticFiles(directory="generated"),
    name="generated",
)

origins = [
    "http://localhost:5173",
    "https://airw.waleedimran.me"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    collection_router,
    prefix="/collections",
    tags=["Collections"]
)

app.include_router(
    document_router,
    prefix="/documents",
    tags=["Documents"]
)

app.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"]
)

app.include_router(
    conversation_router,
    prefix="/conversations",
    tags=["Conversations"]
)

@app.get("/")
async def read_root():
    return {
        "message": "AI Research Workspace API"
    }