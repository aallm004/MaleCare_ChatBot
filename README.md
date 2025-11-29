# MaleCare Clinical Trials Chatbot 🏥

AI-powered chatbot that helps cancer patients find relevant clinical trials using BioClinicalBERT NLP models and the ClinicalTrials.gov API.

## 🎯 Overview

MaleCare ChatBot is a full-stack application designed to help cancer patients discover clinical trials that match their specific medical profile. The system uses natural language processing to understand patient queries and matches them with appropriate clinical trials.

### Key Features

- **Patient Intake System**: Structured form to collect patient medical information
- **NLP-Powered Chat**: BioClinicalBERT models for intent classification and entity extraction
- **Clinical Trial Matching**: Integration with ClinicalTrials.gov API
- **Conversation State Management**: Maintains context throughout the conversation
- **Interactive UI**: Modern Next.js/React frontend with real-time chat interface

---

## 🏗️ Architecture

```
MaleCare_ChatBot/
├── backend/              # FastAPI backend service
│   ├── app/             # Application code
│   ├── tests/           # Automated tests
│   └── ML_Code/         # NLP model training
├── clinicaltrials-chatbot/  # Next.js frontend
└── models/              # Trained ML models
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- BioClinicalBERT (NLP models)
- PyTorch & Transformers
- ClinicalTrials.gov API v2

**Frontend:**
- Next.js 16
- React with TypeScript
- Shadcn UI components
- Tailwind CSS

**ML/AI:**
- Intent Classification Model (greeting, find_trials, goodbye)
- Named Entity Recognition (NER) for medical entities

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **pip** (Python package manager)
- **npm** (Node package manager)

### Installation & Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/aallm004/MaleCare_ChatBot.git
cd MaleCare_ChatBot
```

#### 2. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload
```

The backend API will be available at **http://localhost:8000**

#### 3. Frontend Setup (Optional)

```powershell
# Open a new terminal
cd clinicaltrials-chatbot

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at **http://localhost:3000**

---

## 🧪 Testing

### Automated Tests (Recommended)

The backend includes a comprehensive test suite with 8 automated tests covering all major functionality.

```powershell
# Navigate to backend directory
cd backend

# Run all tests
pytest tests/test_endpoints.py -v

# Run with coverage report
pytest tests/test_endpoints.py -v --cov=app --cov-report=html

# Run specific test
pytest tests/test_endpoints.py::test_full_conversation_flow -v -s
```

**Test Coverage:**
- ✅ Health check endpoint
- ✅ Patient intake form submission
- ✅ Message handling and validation
- ✅ Greeting intent recognition
- ✅ Clinical trial search functionality
- ✅ Goodbye intent recognition
- ✅ Session management
- ✅ Full end-to-end conversation flow

### Interactive Testing

#### Option 1: Browser API Documentation (Easiest!)

1. Start the backend server:
   ```powershell
   cd backend
   uvicorn app.main:app --reload
   ```

2. Open your browser and navigate to:
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

3. Click on any endpoint, click "Try it out", fill in the form, and see results!

#### Option 2: PowerShell Test Script

```powershell
# Terminal 1: Start the server
cd backend
uvicorn app.main:app --reload

# Terminal 2: Run test script
cd backend
.\test_api.ps1
```

This script automatically tests all endpoints and displays colorful results.

#### Option 3: Interactive Python Tester

```powershell
# Terminal 1: Start the server
cd backend
uvicorn app.main:app --reload

# Terminal 2: Run interactive tester
cd backend
python interactive_test.py
```

Follow the prompts to:
1. Enter patient information
2. Chat with the bot
3. See trial results in real-time

#### Option 4: Manual API Testing

With the server running, use curl or any HTTP client:

```powershell
# Health check
curl http://localhost:8000/health

# Submit intake form
curl -X POST http://localhost:8000/intake -H "Content-Type: application/json" -d '{\"user_id\":\"test123\",\"cancer_type\":\"breast cancer\",\"stage\":\"stage 2\",\"age\":45,\"sex\":\"female\",\"location\":\"California\"}'

# Send a message
curl -X POST http://localhost:8000/message -H "Content-Type: application/json" -d '{\"user_id\":\"test123\",\"message\":\"Find me trials in Los Angeles\"}'

# End session
curl -X POST http://localhost:8000/end-session -H "Content-Type: application/json" -d '{\"user_id\":\"test123\"}'
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check - verify server is running |
| `/intake` | POST | Submit patient intake form |
| `/message` | POST | Send a chat message to the bot |
| `/end-session` | POST | Clear user session data |

### Example API Flow

```json
// 1. Submit Intake Form
POST /intake
{
  "user_id": "user123",
  "cancer_type": "breast cancer",
  "stage": "stage 2",
  "age": 45,
  "sex": "female",
  "location": "California",
  "comorbidities": ["diabetes"],
  "prior_treatments": ["chemotherapy"]
}

// 2. Send Chat Message
POST /message
{
  "user_id": "user123",
  "message": "Find me clinical trials in Los Angeles"
}

// 3. End Session
POST /end-session
{
  "user_id": "user123"
}
```

---

## 🤖 NLP Models

The chatbot uses two fine-tuned BioClinicalBERT models:

### Intent Classification Model
- **Location**: `models/intent_model/`
- **Purpose**: Classifies user intent into categories
- **Intents**: 
  - `greeting`: "Hello", "Hi there"
  - `find_trials`: "Find me trials", "Show me studies"
  - `goodbye`: "Thanks, bye"

### Named Entity Recognition (NER) Model
- **Location**: `models/ner_model/`
- **Purpose**: Extracts medical entities from user messages
- **Entities**:
  - `CANCER_TYPE`: breast cancer, lung cancer, etc.
  - `LOCATION`: California, New York, etc.
  - `AGE`: numeric age values
  - `SEX`: male, female

### Training the Models (Optional)

```powershell
cd ML_Code
python train_models.py
```

**Note**: The chatbot works without trained models by using fallback logic and intake form context. Training models improves natural language understanding.

---

## 🔧 Recent Changes & Bug Fixes

### Bug Fixes (November 28, 2025)

1. **Fixed NameError in ClinicalTrials API** (`clinicaltrials_api.py`)
   - Changed undefined variable `condition` to `cancer_type`
   - Resolved crash when querying for trials

2. **Fixed NLP Model Loading Paths** (`nlp.py`)
   - Updated relative paths to absolute paths using `pathlib.Path`
   - Added graceful fallback when models don't exist
   - Server no longer crashes if models aren't trained

3. **Fixed Test Import Issues** 
   - Added `conftest.py` for proper pytest configuration
   - Created `tests/__init__.py` to make tests a proper Python package
   - Tests now run correctly from backend directory

### New Features & Improvements

1. **Comprehensive Test Suite**
   - 8 automated tests covering all endpoints
   - Full conversation flow testing
   - Error handling validation

2. **Testing Tools**
   - `interactive_test.py`: Interactive command-line tester
   - `test_api.ps1`: PowerShell script for quick API testing
   - Pytest configuration for easy test execution

3. **Documentation**
   - `backend/README.md`: Detailed backend documentation
   - `backend/TESTING_GUIDE.md`: Complete testing instructions
   - `backend/TESTING_SUMMARY.md`: Test results and findings
   - Updated project-level README (this file)

4. **Improved Requirements**
   - Added all missing dependencies (torch, transformers, pytest)
   - Organized requirements with comments
   - Version pinning for stability

---

## 📁 Project Structure

```
MaleCare_ChatBot/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── core/
│   │   │   └── state.py              # Conversation state management
│   │   ├── routes/
│   │   │   ├── chat.py               # Chat endpoints
│   │   │   └── health.py             # Health check
│   │   ├── services/
│   │   │   ├── nlp.py                # NLP model inference
│   │   │   └── clinicaltrials_api.py # API client
│   │   └── utils/
│   │       └── config.py             # Configuration
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_endpoints.py         # Comprehensive test suite
│   ├── conftest.py                    # Pytest configuration
│   ├── interactive_test.py            # Interactive tester
│   ├── test_api.ps1                   # PowerShell test script
│   ├── requirements.txt               # Python dependencies
│   ├── README.md                      # Backend documentation
│   ├── TESTING_GUIDE.md              # Testing instructions
│   └── TESTING_SUMMARY.md            # Test results
├── clinicaltrials-chatbot/
│   ├── app/
│   │   ├── page.tsx                  # Main chat interface
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── LottiePlayer.tsx
│   │   └── ui/                       # Shadcn UI components
│   ├── package.json
│   └── next.config.ts
├── ML_Code/
│   ├── clinical_trial_nlp_model.py   # Model architecture
│   ├── train_models.py               # Training script
│   ├── intent_training_data.json     # Intent classification data
│   └── ner_training_data.json        # NER training data
├── models/
│   ├── intent_model/                 # Trained intent classifier
│   └── ner_model/                    # Trained NER model
└── README.md                          # This file
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### "uvicorn: The term 'uvicorn' is not recognized"

**Solution**: Install dependencies
```powershell
cd backend
pip install -r requirements.txt
```

#### "ModuleNotFoundError: No module named 'app'"

**Solution**: Run pytest from the backend directory, not the tests directory
```powershell
cd backend  # Not backend/tests
pytest tests/test_endpoints.py -v
```

#### "Cannot connect to server" (when testing)

**Solution**: Make sure the server is running in a separate terminal
```powershell
# Terminal 1
uvicorn app.main:app --reload

# Terminal 2
python interactive_test.py
```

#### "Port 8000 already in use"

**Solution**: Either close the existing server or use a different port
```powershell
uvicorn app.main:app --reload --port 8001
```

#### "NLP models not loaded"

**Solution**: This is expected if you haven't trained the models. The chatbot will work with fallback logic. To train models:
```powershell
cd ML_Code
python train_models.py
```

---

## 📊 Test Results

### Latest Test Run (November 28, 2025)

```
======================== test session starts =========================
collected 8 items

tests/test_endpoints.py::test_health PASSED                   [ 12%]
tests/test_endpoints.py::test_intake_submission PASSED        [ 25%]
tests/test_endpoints.py::test_message_without_intake PASSED   [ 37%]
tests/test_endpoints.py::test_greeting_intent PASSED          [ 50%]
tests/test_endpoints.py::test_find_trials_intent PASSED       [ 62%]
tests/test_endpoints.py::test_goodbye_intent PASSED           [ 75%]
tests/test_endpoints.py::test_end_session PASSED              [ 87%]
tests/test_endpoints.py::test_full_conversation_flow PASSED   [100%]

===================== 8 passed in 21.64s =========================
```

**All tests passing!** ✅

---

## 🔮 Future Enhancements

### Planned Features

- [ ] Persistent database for conversation history (PostgreSQL/MongoDB)
- [ ] Real-time integration with ClinicalTrials.gov API
- [ ] Advanced eligibility matching algorithm
- [ ] Multi-turn conversation refinement
- [ ] User authentication and authorization
- [ ] Patient dashboard for saved trials
- [ ] Email notifications for new matching trials
- [ ] Multi-language support
- [ ] Voice interface integration

### Deployment

- [ ] Docker containerization
- [ ] Azure/AWS deployment configuration
- [ ] CI/CD pipeline setup
- [ ] Production environment configuration
- [ ] Load balancing and scaling
- [ ] Monitoring and logging (Application Insights)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Team

MaleCare ChatBot Development Team

---

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the [TESTING_GUIDE.md](backend/TESTING_GUIDE.md) for detailed testing help
- Review [backend/README.md](backend/README.md) for backend-specific documentation

---

## 🙏 Acknowledgments

- BioClinicalBERT model by Emily Alsentzer et al.
- ClinicalTrials.gov for providing the clinical trials database
- FastAPI and Next.js communities

---

## 📝 Changelog

### v0.2.0 - November 28, 2025 (Steve's Updates)

**Bug Fixes:**
- Fixed NameError in `clinicaltrials_api.py` (condition → cancer_type)
- Fixed NLP model loading paths to use absolute paths
- Fixed pytest import issues with conftest.py

**New Features:**
- Added comprehensive automated test suite (8 tests)
- Created interactive testing script (interactive_test.py)
- Added PowerShell test script (test_api.ps1)
- Improved error handling and graceful fallbacks

**Documentation:**
- Complete backend README with testing instructions
- Detailed TESTING_GUIDE.md
- TESTING_SUMMARY.md with results
- Updated main README with full setup instructions

**Dependencies:**
- Added missing ML dependencies (torch, transformers)
- Added testing dependencies (pytest, pytest-cov)
- Organized requirements.txt with comments

### v0.1.0 - Initial Release

- Basic chatbot functionality
- FastAPI backend with NLP integration
- Next.js frontend
- BioClinicalBERT model integration
- Basic intake form processing

---

**Made with ❤️ for cancer patients seeking clinical trials**