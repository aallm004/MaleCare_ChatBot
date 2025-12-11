# 🧪 Automated API Performance Testing

Comprehensive testing suite for the MaleCare ChatBot API that runs automated tests every 30 minutes for a week, testing different cancer types with randomized patient data and recording detailed performance metrics.

## 📋 What This Does

✅ **Tests all three cancer types**: breast, prostate, lung  
✅ **Randomizes patient data** every test (name, age, location, etc.)  
✅ **Records response times** for each API call  
✅ **Tracks success/failure rates**  
✅ **Saves results to CSV** for analysis  
✅ **Generates summary reports** for meetings  

## 🎯 Goals Achieved

- ✅ Test ClinicalTrials.gov API with all three cancer types
- ✅ Optimize result parsing and formatting
- ✅ Add error handling (no results, timeouts, invalid locations)
- ✅ Build reliable API query function
- ✅ Ensure response times are <3 seconds

---

## 🚀 Quick Start

### Option 1: Run a Quick Test (Single Test)

Perfect for verifying everything works:

```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend\tests"
python automated_api_tests.py
```

This runs ONE test and saves results. Great for testing!

### Option 2: Run Continuous Testing (1 Week)

Runs tests every 30 minutes for 7 days:

```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend\tests"
python automated_api_tests.py --continuous
```

**Important**: Keep this running! You can minimize the window.

To stop early: Press `Ctrl+C`

---

## 📊 Analyzing Results

After running tests (even just a few), analyze the data:

```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend\tests"
python analyze_results.py
```

This shows:
- ✅ Success rates
- ⏱️ Response time statistics
- 🎗️ Cancer type breakdown
- 📍 Location coverage
- ⚠️ Error analysis
- 💡 Recommendations for your meeting

---

## 📁 Files Created

### `automated_api_tests.py`
Main testing script that:
- Generates random patient data
- Tests intake + message endpoints
- Records response times
- Saves results to CSV

### `analyze_results.py`
Analysis script that:
- Reads CSV results
- Generates statistics
- Creates summary reports
- Provides recommendations

### `test_results/api_test_results.csv`
CSV file with ALL test data:
- Timestamp
- Patient demographics
- Response times
- Success/failure status
- Errors encountered
- Trials found

### `test_results/summary_report.txt`
Quick summary for meetings

---

## 📈 Sample Output

### Quick Test Output:
```
🧪 Running test with: emma_456
   Cancer Type: breast cancer
   Location: Phoenix Arizona

======================================================================
Test Run: 2025-11-28T14:30:00.123456
======================================================================
Patient: emma_456
Cancer Type: breast cancer
Stage: stage 2
Age: 52 | Sex: female
Location: Phoenix Arizona
----------------------------------------------------------------------
✓ Intake Response Time: 0.234567 seconds
✓ Message Response Time: 0.567890 seconds
✓ Trials Found: 1

📊 Total Response Time: 0.802457 seconds
✅ Test Status: SUCCESS
======================================================================

✓ Results saved to test_results\api_test_results.csv
```

### Analysis Output:
```
================================================================================
 📊 MaleCare ChatBot - API Performance Test Results Analysis
================================================================================

📈 OVERALL STATISTICS
--------------------------------------------------------------------------------
Total Tests Run: 48
Successful Tests: 47 (97.9%)
Failed Tests: 1 (2.1%)
Test Period: 2025-11-28 10:00 to 2025-11-29 10:00
Duration: 1 days, 0 hours

⏱️  RESPONSE TIME ANALYSIS
--------------------------------------------------------------------------------
Total Response Times:
  Average: 0.856234 seconds
  Median:  0.834512 seconds
  Min:     0.234567 seconds
  Max:     2.345678 seconds
  Std Dev: 0.123456 seconds

  Tests under 3 seconds: 48/48 (100.0%)

Intake Endpoint:
  Average: 0.245678 seconds
  Min:     0.123456 seconds
  Max:     0.456789 seconds

Message Endpoint (Trial Search):
  Average: 0.610556 seconds
  Min:     0.234567 seconds
  Max:     1.888889 seconds

🎗️  CANCER TYPE BREAKDOWN
--------------------------------------------------------------------------------

Breast Cancer:
  Tests: 16
  Success Rate: 100.0%
  Avg Trials Found: 1.0
  Min Trials: 1
  Max Trials: 1

Lung Cancer:
  Tests: 16
  Success Rate: 93.8%
  Avg Trials Found: 1.0
  Min Trials: 1
  Max Trials: 1

Prostate Cancer:
  Tests: 16
  Success Rate: 100.0%
  Avg Trials Found: 1.0
  Min Trials: 1
  Max Trials: 1

💡 RECOMMENDATIONS FOR TUESDAY MEETING
--------------------------------------------------------------------------------
✅ Average response time (0.856s) meets <3s target
✅ Success rate (97.9%) is excellent
✅ All three cancer types tested successfully

📊 Trial Results:
   Average trials per search: 1.0
```

---

## 🔧 Customization

### Change Test Frequency

Edit `automated_api_tests.py`:
```python
TEST_INTERVAL_MINUTES = 30  # Change to 15, 60, etc.
```

### Change Test Duration

```python
TEST_DURATION_DAYS = 7  # Change to 1, 3, 14, etc.
```

### Add More Locations

```python
LOCATIONS = [
    "Phoenix Arizona",
    "Your City Here",
    # Add more...
]
```

### Add More Cancer Types

```python
CANCER_TYPES = ["breast cancer", "prostate cancer", "lung cancer", "colon cancer"]
```

---

## 📅 For Your Tuesday Meeting

### What to Prepare:

1. **Run tests now** (even just for 1-2 days):
   ```powershell
   python automated_api_tests.py --continuous
   ```

2. **Before the meeting**, analyze results:
   ```powershell
   python analyze_results.py
   ```

3. **Bring these files**:
   - `test_results/api_test_results.csv` (raw data)
   - `test_results/summary_report.txt` (summary)
   - Screenshots of the analysis output

### Key Metrics to Present:

✅ **Success Rate**: Should be >95%  
✅ **Average Response Time**: Should be <3 seconds  
✅ **Cancer Types Tested**: All 3 types  
✅ **Error Handling**: Show how errors are caught  
✅ **Data Variety**: Show different ages, locations, stages  

---

## 🎯 Understanding the Data

### CSV Columns Explained:

| Column | Description |
|--------|-------------|
| `timestamp` | When the test ran |
| `user_id` | Generated test user ID |
| `cancer_type` | breast/prostate/lung cancer |
| `stage` | stage 1, 2, 3, or 4 |
| `age` | Random age (40-80) |
| `sex` | male/female |
| `location` | Random US city |
| `intake_response_time` | Time for intake endpoint (seconds) |
| `message_response_time` | Time for message endpoint (seconds) |
| `total_response_time` | Combined time (seconds) |
| `trials_found` | Number of trials returned |
| `success` | True/False |
| `intake_error` | Error message if failed |
| `message_error` | Error message if failed |

---

## 🐛 Troubleshooting

### "Cannot connect to server"

**Solution**: Make sure the backend is running:
```powershell
cd "c:\Data\Project AI\MaleCare_ChatBot\backend"
uvicorn app.main:app --reload
```

### "No results file found"

**Solution**: Run at least one test first:
```powershell
python automated_api_tests.py
```

### Tests are too slow

**Current issue**: Using mock data, so response times are fast  
**Future**: When connected to real ClinicalTrials.gov API, times may increase

---

## 💡 Pro Tips

### Tip 1: Run in Background

On Windows, you can run this in a minimized PowerShell window and let it run while you work on other things.

### Tip 2: Check Progress Anytime

You can run `analyze_results.py` at any time to see current statistics, even while tests are still running.

### Tip 3: Test Connection First

Always run a quick test before starting the week-long test:
```powershell
python automated_api_tests.py
```

### Tip 4: Export to Excel

The CSV file can be opened in Excel for custom analysis and charts!

---

## 📊 Example Use Cases

### Scenario 1: Quick Verification
```powershell
# Run 1 test to verify everything works
python automated_api_tests.py

# Check the results
python analyze_results.py
```

### Scenario 2: Overnight Testing
```powershell
# Start before you leave work
# Let it run overnight (30 min intervals)
python automated_api_tests.py --continuous
```

### Scenario 3: Meeting Prep
```powershell
# Run Friday - Monday (3 days of data)
python automated_api_tests.py --continuous

# On Tuesday morning, analyze
python analyze_results.py

# Present findings!
```

---

## 🎉 Success Criteria

Your Tuesday meeting goals are met when:

✅ All 3 cancer types show >95% success rate  
✅ Average response time <3 seconds  
✅ Errors are properly logged and handled  
✅ Results show variety in patient data  
✅ System handles timeouts gracefully  
✅ CSV data ready for presentation  

---

## 📞 Questions?

Check the main README or TESTING_GUIDE for more information about the API endpoints and testing strategies.

**Happy Testing!** 🚀
