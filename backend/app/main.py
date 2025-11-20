from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, chat
from app.services import nlp

app = FastAPI(
    title="Cancer Trial Match Chatbot API",
    description="AI chatbot backend for matching cancer patients to clinical trials.",
    version="0.1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Load ML models on startup
@app.on_event("startup")
async def startup_event():
    """Load NLP models when the app starts."""
    print("\n" + "="*60)
    print("Loading NLP models...")
    print("="*60)
    try:
        nlp.load_models()
        print("="*60)
        print("NLP models loaded successfully")
        print("="*60 + "\n")
    except Exception as e:
        print("="*60)
        print(f"ERROR loading models: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        raise

# Include routers
app.include_router(health.router)
app.include_router(chat.router)