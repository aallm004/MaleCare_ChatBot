# MaleCare Clinical Trials Chatbot - Backend

AI-powered chatbot that helps cancer patients find relevant clinical trials using BioClinicalBERT NLP models.

## 🏗️ Architecture

- **Framework**: FastAPI (Python)
- **NLP Models**: BioClinicalBERT for intent classification and entity extraction
- **API**: ClinicalTrials.gov API v2
- **State Management**: In-memory session storage

## 📋 Features

- Patient intake form processing
- Intent classification (greeting, find_trials, goodbye)
- Named Entity Recognition (NER) for cancer type, location, age, sex
- Clinical trial search and matching
- Conversation state management

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```powershell
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```powershell
# From the backend directory
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

### 1. Automated Tests (Recommended)

Run the comprehensive test suite:

```powershell
# From the backend directory
pytest tests/test_endpoints.py -v
```

Run specific tests:
```powershell
# Test health endpoint
pytest tests/test_endpoints.py::test_health -v

# Test full conversation flow
pytest tests/test_endpoints.py::test_full_conversation_flow -v -s
```

Run with coverage:
```powershell
pytest tests/test_endpoints.py -v --cov=app --cov-report=html
```

### 2. Interactive Testing

Start the server, then run the interactive tester:

```powershell
# Terminal 1: Start the server
uvicorn app.main:app --reload

# Terminal 2: Run interactive tester
python interactive_test.py
```

The interactive tester will:
1. Prompt you to enter patient information
2. Allow you to chat with the bot
3. Show real-time responses and trial results

### 3. Manual API Testing

Use curl, Postman, or any HTTP client:

**Health Check:**
```powershell
curl http://localhost:8000/health
```

**Submit Intake Form:**
```powershell
curl -X POST http://localhost:8000/intake `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": "test123",
    "cancer_type": "breast cancer",
    "stage": "stage 2",
    "age": 45,
    "sex": "female",
    "location": "California",
    "comorbidities": ["diabetes"],
    "prior_treatments": ["chemotherapy"]
  }'
```

**Send a Message:**
```powershell
curl -X POST http://localhost:8000/message `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": "test123",
    "message": "Find me clinical trials in Los Angeles"
  }'
```

**End Session:**
```powershell
curl -X POST http://localhost:8000/end-session `
  -H "Content-Type: application/json" `
  -d '{"user_id": "test123"}'
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   └── state.py         # Conversation state management
│   ├── routes/
│   │   ├── chat.py          # Chat endpoints (/intake, /message, /end-session)
│   │   └── health.py        # Health check endpoint
│   ├── services/
│   │   ├── nlp.py           # NLP model loading and inference
│   │   └── clinicaltrials_api.py  # ClinicalTrials.gov API client
│   └── utils/
│       └── config.py        # Configuration settings
├── tests/
│   ├── __init__.py
│   └── test_endpoints.py    # Comprehensive test suite
├── conftest.py              # Pytest configuration
├── interactive_test.py      # Interactive testing script
└── requirements.txt         # Python dependencies
```

## 🤖 NLP Models

The chatbot uses two BioClinicalBERT models:

### Intent Classification Model
- **Location**: `models/intent_model/`
- **Purpose**: Classifies user intent (greeting, find_trials, goodbye)
- **Base Model**: emilyalsentzer/Bio_ClinicalBERT

### Named Entity Recognition (NER) Model
- **Location**: `models/ner_model/`
- **Purpose**: Extracts entities (cancer type, location, age, sex)
- **Labels**: B-CANCER_TYPE, I-CANCER_TYPE, B-LOCATION, etc.

### Training Models

To train the NLP models:

```powershell
cd ML_Code
python train_models.py
```

**Note**: The chatbot will work without trained models (using fallback logic), but intent classification and entity extraction will be limited.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
CLINICALTRIALS_API_BASE=https://clinicaltrials.gov/api/v2
```

## 📊 Testing Coverage

The test suite covers:

- ✅ Health check endpoint
- ✅ Intake form submission
- ✅ Message handling without intake (error case)
- ✅ Greeting intent recognition
- ✅ Find trials intent with API call
- ✅ Goodbye intent recognition
- ✅ Session termination
- ✅ Full conversation flow (end-to-end)

## 🐛 Troubleshooting

### Models Not Loading

If you see "Intent model not loaded" or "NER model not loaded" warnings:

1. Check that models exist in `models/intent_model/` and `models/ner_model/`
2. Train models using `python ML_Code/train_models.py`
3. The chatbot will still work with fallback logic

### Import Errors

If you get "ModuleNotFoundError: No module named 'app'":

1. Make sure you're running pytest from the `backend/` directory, not `backend/tests/`
2. Check that `conftest.py` exists in the `backend/` directory

### Port Already in Use

If port 8000 is already in use:

```powershell
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## 🔮 Future Improvements

- [ ] Persistent database for conversation history
- [ ] Real-time clinical trial matching
- [ ] Multi-turn conversation refinement
- [ ] Patient eligibility scoring
- [ ] Integration with real ClinicalTrials.gov API
- [ ] User authentication and authorization
- [ ] Deployment configuration (Docker, Azure)

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/intake` | POST | Submit patient intake form |
| `/message` | POST | Send a chat message |
| `/end-session` | POST | Clear session data |

## 📖 Example Test Output

```
============================================================
FULL CONVERSATION FLOW TEST
============================================================

1. Submitting intake form...
   Bot: Thank you for sharing that information with me. How can I help you find clinical trials today?

2. Saying hello...
   Bot: Hello! How can I help you find clinical trials today?

3. Asking for clinical trials...
   Bot: Here are some breast cancer clinical trials in California:
   Found 1 trials

4. Ending conversation...
   Bot: Goodbye! Feel free to return anytime you need help finding clinical trials.

5. Clearing session...
   ✓ Session cleared

============================================================
CONVERSATION FLOW COMPLETE
============================================================
```

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributors

MaleCare ChatBot Development Team
