# Weekend Monitoring Guide

## Quick Start

### Friday Evening - Start Monitoring
```bash
# 1. Start the backend server (keep running)
cd backend
python -m uvicorn app.main:app --port 8000

# 2. In a NEW terminal, start monitoring
cd backend/tests/API_Testing
python weekend_monitoring.py
```

The monitoring will:
- Run every 30 minutes automatically
- Test different patient scenarios randomly
- Log everything to `weekend_api_monitoring.csv`
- Keep running until you stop it (Ctrl+C on Monday)

### Monday Morning - View Results
```bash
cd backend/tests/API_Testing
python analyze_weekend_results.py
```

## What Gets Logged

Each test records:
- **Timestamp** - When the test ran
- **Patient Info** - Name, cancer type, location, age, etc.
- **API Performance** - Query time in seconds
- **Results** - Number of trials found
- **Errors** - Any issues encountered
- **Sample Trial** - First trial NCT ID, title, facility

## Patient Scenarios

The monitoring rotates through 12 realistic scenarios:
- **Major Cities:** Boston, LA, NYC, Chicago, Houston, Phoenix, Philadelphia, San Antonio, San Diego, Dallas
- **Small Towns:** Siloam Springs AR, Bend OR (tests nationwide fallback)
- **Cancer Types:** Prostate, Breast, Lung, Colorectal, Ovarian, Melanoma, Pancreatic
- **Ages:** 43-69 years old
- **Stages:** 1-4

## Files Created

- `weekend_api_monitoring.csv` - Raw test data (one row per test)
- Console logs show real-time progress

## Expected Results

**Per Test:**
- Query time: 0.5-3 seconds
- Trials found: 5-10 (or nationwide if small town)
- HTTP 200 status

**Over Weekend (30-min intervals):**
- ~96 tests (48 hours × 2 tests/hour)
- Mix of local and nationwide results
- Performance trends visible

## Troubleshooting

**Server not running?**
```bash
# Check if server is up
curl http://localhost:8000/health
```

**CSV file not being created?**
- Check permissions in `tests/API_Testing/` folder
- Run monitor with `python -u weekend_monitoring.py` for unbuffered output

**Want to test now?**
```bash
# Run one test immediately (30 sec timeout)
python weekend_monitoring.py
# Press Ctrl+C after first test completes
```

## Monday Review Checklist

✅ Run `python analyze_weekend_results.py`  
✅ Check for any errors or timeouts  
✅ Review average query times  
✅ Verify nationwide fallback worked  
✅ Confirm trial variety (different NCT IDs)  

## Sample CSV Output
```
Timestamp,Patient_Name,Cancer_Type,Location,API_Query_Time_Seconds,Trials_Found,Sample_Trial_NCT_ID
2025-12-06T18:00:00,John Smith,prostate cancer,Boston Massachusetts,1.234,10,NCT05512065
2025-12-06T18:30:00,Mary Johnson,breast cancer,Los Angeles California,0.987,10,NCT06484140
```
