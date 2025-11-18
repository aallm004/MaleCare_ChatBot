python
from fastapi import FastAPI
from app.routes import health, chat

app = FastAPI(
    title="Cancer Trial Match Chatbot API",
    description="AI chatbot backend for matching cancer patients to clinical trials.",
    version="0.1.0"
)

# Include routers
app.include_router(health.router)
app.include_router(chat.router)