# Real API Integration Guide# 🔗 Real ClinicalTrials.gov API Integration Guide



## Overview## 📖 What's Currently Happening (Mock Data)

The MaleCare ChatBot uses the **real** ClinicalTrials.gov API v2, returning actual recruiting clinical trials based on cancer type and location.

Right now, the system returns **fake/placeholder trials** instead of real data from ClinicalTrials.gov.

## API Details

- **Base URL:** `https://clinicaltrials.gov/api/v2/studies`### Current Behavior:

- **Authentication:** None required (public API)```python

- **Documentation:** https://clinicaltrials.gov/data-api/api# In clinicaltrials_api.py - lines 27-37

return [

## Parameters    {

```        "nct_id": "NCT12345678",

query.cond           - Cancer type (e.g., "breast cancer")        "title": f"A Study for {cancer_type} in {location}",

query.locn           - Location as "City, STATE" (e.g., "Boston, MA")        "phase": "Phase 2",

filter.overallStatus - Set to "RECRUITING"        "status": "Recruiting",

pageSize             - Number of results (default: 10)        "location": location,

```        "link": f"https://clinicaltrials.gov/study/NCT12345678"

    }

**Location Format:** Must be `"City, STATE"` with 2-letter state abbreviation.]

- ✅ Correct: `"Boston, MA"````

- ❌ Wrong: `"Boston Massachusetts"` (gets converted automatically)

**Result**: Every search returns the same fake trial with made-up NCT ID.

## Implementation

---

### File: `backend/app/services/clinicaltrials_api.py`

## 🎯 What We Need to Do

**Key Function:**

```pythonReplace the mock data with **real API calls** to ClinicalTrials.gov's public API.

async def search_clinical_trials(cancer_type: str, location: Optional[str] = None):

    # Convert location: "Boston Massachusetts" → "Boston, MA"### The Real API:

    formatted_location = format_location_for_api(location)- **Base URL**: `https://clinicaltrials.gov/api/v2`

    - **Documentation**: https://clinicaltrials.gov/data-api/api

    # Query real API- **No API Key Required**: It's a public API! ✅

    params = {- **Rate Limits**: Be respectful, don't spam requests

        "query.cond": cancer_type,

        "query.locn": formatted_location,---

        "filter.overallStatus": "RECRUITING",

        "pageSize": 10## 🛠️ Step-by-Step Implementation

    }

    ### Step 1: Understanding the API Structure

    async with httpx.AsyncClient(timeout=10.0) as client:

        response = await client.get(base_url, params=params)The ClinicalTrials.gov API v2 uses this structure:

        return parse_trials(response.json())

```**Endpoint**: `GET https://clinicaltrials.gov/api/v2/studies`



## Testing**Query Parameters**:

```bash- `query.cond`: Condition/disease (e.g., "breast cancer")

# Interactive tester- `query.term`: General search term

python tests/API_Testing/interactive_test_real_api.py- `filter.overallStatus`: Status (e.g., "RECRUITING")

- `filter.geo`: Location search (e.g., "distance(37.7749,-122.4194,50mi)")

# Run all tests- `pageSize`: Number of results (default 10, max 1000)

pytest tests/API_Testing/ -v- `format`: Response format (json, csv)

```

**Example Request**:

## Verified Results```

- **Breast Cancer, Boston MA:** 10 trials from MGH, Dana-Farber, etc.https://clinicaltrials.gov/api/v2/studies?query.cond=breast+cancer&filter.overallStatus=RECRUITING&pageSize=5&format=json

- **Prostate Cancer, Los Angeles CA:** 10 trials from UCLA, Cedars-Sinai, etc.```

- **Lung Cancer, New York NY:** 10 trials from MSK, NYU, etc.

### Step 2: Understanding the API Response

## Troubleshooting

The API returns JSON with this structure:

**No results?**

- Verify location includes state: `"Boston Massachusetts"` or `"Boston, MA"````json

- Use general cancer terms: `"breast cancer"` not `"stage IV metastatic breast cancer"`{

  "studies": [

**API timeout?**    {

- Increase timeout: `httpx.AsyncClient(timeout=20.0)`      "protocolSection": {

        "identificationModule": {

## Rollback to Mock Data          "nctId": "NCT05123456",

```bash          "officialTitle": "Study of XYZ in Breast Cancer Patients",

cd backend/app/services          "briefTitle": "XYZ for Breast Cancer"

cp clinicaltrials_api_BACKUP.py clinicaltrials_api.py        },

```        "statusModule": {

          "overallStatus": "RECRUITING",

## Files          "startDateStruct": {

- **Implementation:** `backend/app/services/clinicaltrials_api.py`            "date": "2024-01-15"

- **Backup (Mock):** `backend/app/services/clinicaltrials_api_BACKUP.py`          }

- **Tests:** `backend/tests/API_Testing/`        },

        "designModule": {
          "phases": ["PHASE2"]
        },
        "contactsLocationsModule": {
          "locations": [
            {
              "facility": "Memorial Hospital",
              "city": "New York",
              "state": "New York",
              "zip": "10021",
              "country": "United States"
            }
          ]
        }
      }
    }
  ],
  "totalCount": 1234
}
```

---

## 💻 Implementation Code

I'll create the updated `clinicaltrials_api.py` file that uses the **real API**.

### Key Changes:

1. **Remove mock data**
2. **Make actual API calls** using `httpx`
3. **Parse the real API response** structure
4. **Handle errors** gracefully (no results, API down, etc.)
5. **Add location geocoding** (convert city names to coordinates)

---

## 🚀 What You'll Get

### Before (Mock):
```
User: "Find trials for breast cancer in Boston"
→ Returns: 1 fake trial (NCT12345678) every time
```

### After (Real API):
```
User: "Find trials for breast cancer in Boston"
→ Returns: 10-50+ REAL trials from ClinicalTrials.gov database
→ Real NCT IDs, real titles, real locations, real contact info
```

---

## 📋 Implementation Checklist

- [ ] Update `clinicaltrials_api.py` to use real API
- [ ] Add error handling for API failures
- [ ] Add location geocoding (optional but recommended)
- [ ] Test with real queries
- [ ] Update response formatting
- [ ] Add caching (optional, for better performance)

---

## ⚠️ Important Considerations

### 1. **Rate Limiting**
- The API is public but has rate limits
- Don't make hundreds of requests per second
- Consider adding caching for repeated searches

### 2. **Location Handling**
The API prefers:
- Geographic coordinates: `filter.geo=distance(37.7749,-122.4194,50mi)`
- Or specific cities: `filter.geo=United States:Massachusetts:Boston`

### 3. **Response Time**
- Real API calls will be **slower** than mock data
- Expect 1-3 seconds per search (vs instant mock)
- This is normal and expected!

### 4. **Data Quality**
- Real trials may have missing fields
- Need robust error handling
- Some trials may not have contact info

---

## 🎯 Next Steps

### Option 1: Basic Implementation (15 minutes)
- Uncomment the API call
- Parse basic trial info
- Return real results

### Option 2: Full Implementation (1-2 hours)
- Full error handling
- Location geocoding
- Response caching
- Rich trial details
- Contact information extraction

### Option 3: Production-Ready (Half day)
- All of Option 2, plus:
- Retry logic
- Fallback strategies
- Logging and monitoring
- Performance optimization

---

## 📝 Testing the Real API

### Quick Test (Command Line):

```powershell
# Test the API directly
curl "https://clinicaltrials.gov/api/v2/studies?query.cond=breast+cancer&filter.overallStatus=RECRUITING&pageSize=3&format=json"
```

### Test in Python:

```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://clinicaltrials.gov/api/v2/studies",
            params={
                "query.cond": "breast cancer",
                "filter.overallStatus": "RECRUITING",
                "pageSize": 3,
                "format": "json"
            }
        )
        print(response.json())

asyncio.run(test_api())
```

---

## 🔍 Example: What Real Data Looks Like

### Mock Data (Current):
```json
{
  "nct_id": "NCT12345678",
  "title": "A Study for breast cancer in Boston Massachusetts",
  "phase": "Phase 2",
  "status": "Recruiting",
  "location": "Boston Massachusetts"
}
```

### Real Data (After Integration):
```json
{
  "nct_id": "NCT05123456",
  "title": "Pembrolizumab and Chemotherapy in Triple-Negative Breast Cancer",
  "phase": "Phase 3",
  "status": "Recruiting",
  "sponsor": "Dana-Farber Cancer Institute",
  "locations": [
    {
      "facility": "Dana-Farber Cancer Institute",
      "city": "Boston",
      "state": "Massachusetts",
      "zip": "02215",
      "contact": {
        "name": "Clinical Trials Office",
        "phone": "617-555-1234"
      }
    }
  ],
  "eligibility": {
    "minimumAge": "18 Years",
    "sex": "ALL"
  }
}
```

---

## 💡 Benefits of Real API Integration

✅ **Accurate Results**: Real, up-to-date clinical trials  
✅ **More Trials**: Dozens/hundreds instead of 1 fake trial  
✅ **Better Matching**: Location-based search actually works  
✅ **Contact Info**: Users can actually contact trial coordinators  
✅ **Professional**: System is actually useful, not just a demo  
✅ **Data Freshness**: Trials update as studies open/close  

---

## 🎓 Learning Resources

- **API Docs**: https://clinicaltrials.gov/data-api/api
- **API Explorer**: https://clinicaltrials.gov/data-api/api
- **Field Definitions**: https://clinicaltrials.gov/data-api/about-api/study-data-structure

---

**Ready to implement? Let me know and I'll create the updated code!** 🚀
