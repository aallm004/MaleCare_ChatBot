# API Testing Tools

## Quick Start

**Interactive Testing (Recommended)**
```bash
python tests/API_Testing/interactive_test_real_api.py
```
Enter patient details and get instant trial results with clickable links.

## Test Files

### Interactive Tools
- `interactive_test_real_api.py` - Console-based tester with colored output and auto-display

### Weekend Monitoring (NEW!)
- `weekend_monitoring.py` - Continuous monitoring every 30 minutes
- `analyze_weekend_results.py` - Monday morning results analyzer
- `WEEKEND_MONITORING_GUIDE.md` - Complete setup instructions

**Start Weekend Monitoring:**
```bash
python tests/API_Testing/weekend_monitoring.py
```
Runs every 30 minutes, logs to CSV, simulates 12 realistic patient scenarios.

### Demos
- `demo_chatbot.py` - Pre-filled scenarios (breast/prostate/lung cancer)
- `demo_fallback.py` - Nationwide fallback demonstration
- `test_full_chatbot.py` - Full chatbot flow test

### Unit Tests
- `test_real_api.py` - Basic API connectivity verification
- `test_simple_api.py` - Parameter format validation
- `test_integration.py` - End-to-end integration tests
- `test_fallback.py` - Nationwide fallback feature tests

## Features Tested
- ✅ Real ClinicalTrials.gov API integration
- ✅ Location formatting (City, STATE)
- ✅ Cancer type search (query.cond)
- ✅ Nationwide fallback (small towns get all US trials)
- ✅ Clickable NCT links
- ✅ Continuous monitoring with CSV logging

## Run All Tests
```bash
pytest tests/API_Testing/ -v
```
