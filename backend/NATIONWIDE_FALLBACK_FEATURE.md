# Nationwide Fallback Feature

## Overview
When a user searches from a small town with no local trials, the system automatically searches all US recruiting trials instead.

## How It Works

1. **First Search:** Local trials based on patient's city/state
2. **If Empty:** Automatically search nationwide (no location filter)
3. **Result:** User always gets trial options, regardless of location

## Implementation

### File: `backend/app/services/clinicaltrials_api.py`

```python
async def search_clinical_trials(cancer_type: str, location: Optional[str] = None):
    # Try local search first
    trials = await _search_with_location(cancer_type, location)
    
    # If no local trials, search nationwide
    if not trials and location:
        logger.info(f"No local trials for {location}, searching nationwide")
        trials = await _search_with_location(cancer_type, location=None)
        
        # Mark trials as nationwide
        for trial in trials:
            trial["is_nationwide"] = True
    
    return trials
```

## User Experience

**Small Town Example (Siloam Springs, AR):**
```
Patient: "I'm in Siloam Springs Arkansas"
Result: No local trials found → Nationwide search returns 10 trials
Display: "Showing trials from across the United States"
```

**Large City Example (Boston, MA):**
```
Patient: "I'm in Boston Massachusetts"  
Result: 10 local trials found
Display: Normal local results
```

## Benefits
- ✅ 100% success rate (users always get results)
- ✅ No "no trials found" dead ends
- ✅ Trials show actual locations for user decision-making
- ✅ Transparent messaging (users know when viewing nationwide results)

## Testing
```bash
# Test fallback feature
python tests/API_Testing/test_fallback.py

# Demo fallback
python tests/API_Testing/demo_fallback.py
```

## Expected Behavior
- **Local trials available:** Returns location-specific results
- **No local trials:** Returns nationwide results with flag `is_nationwide: true`
- **Always:** User gets actionable trial information
