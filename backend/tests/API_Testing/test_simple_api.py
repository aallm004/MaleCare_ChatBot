"""
Simple, focused test of ClinicalTrials.gov API
Tests what actually works based on real API behavior
"""

import httpx
import asyncio


async def test_working_api_calls():
    """Test the API calls that we know work"""
    
    print("\n" + "="*70)
    print("🧪 ClinicalTrials.gov API - Working Examples")
    print("="*70 + "\n")
    
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    
    # Test 1: Basic cancer search (NO location filter)
    print("Test 1: Search for breast cancer trials (no location)")
    print("-" * 70)
    
    params = {
        "query.cond": "breast cancer",
        "filter.overallStatus": "RECRUITING",
        "pageSize": 5,
        "format": "json"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(base_url, params=params)
        data = response.json()
        
        studies = data.get("studies", [])
        print(f"✅ Found {len(studies)} trials in response")
        
        if studies:
            study = studies[0]
            protocol = study.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            print(f"   Sample: {identification.get('nctId')} - {identification.get('briefTitle', '')[:60]}...")
    
    print()
    
    # Test 2: With location using query.locn
    print("Test 2: Search with location using query.locn")
    print("-" * 70)
    
    params = {
        "query.cond": "breast cancer",
        "query.locn": "Boston, MA",  # This format works!
        "filter.overallStatus": "RECRUITING",
        "pageSize": 5,
        "format": "json"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(base_url, params=params)
        data = response.json()
        
        studies = data.get("studies", [])
        print(f"✅ Found {len(studies)} trials near Boston, MA")
        
        if studies:
            study = studies[0]
            protocol = study.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            contacts = protocol.get("contactsLocationsModule", {})
            locations = contacts.get("locations", [])
            
            print(f"   NCT ID: {identification.get('nctId')}")
            print(f"   Title: {identification.get('briefTitle', '')[:70]}")
            if locations:
                loc = locations[0]
                print(f"   Location: {loc.get('facility')}, {loc.get('city')}, {loc.get('state')}")
    
    print()
    
    # Test 3: Different cancer types
    print("Test 3: Different cancer types")
    print("-" * 70)
    
    cancer_types = ["breast cancer", "prostate cancer", "lung cancer"]
    
    for cancer in cancer_types:
        params = {
            "query.cond": cancer,
            "filter.overallStatus": "RECRUITING",
            "pageSize": 1,
            "format": "json"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params=params)
            data = response.json()
            studies = data.get("studies", [])
            print(f"   {cancer:20s} → {len(studies)} trials found")
    
    print()
    
    # Test 4: Different locations
    print("Test 4: Different US cities")
    print("-" * 70)
    
    cities = [
        "Boston, MA",
        "New York, NY",
        "Los Angeles, CA",
        "Chicago, IL",
        "Houston, TX"
    ]
    
    for city in cities:
        params = {
            "query.cond": "cancer",
            "query.locn": city,
            "filter.overallStatus": "RECRUITING",
            "pageSize": 1,
            "format": "json"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params=params)
            data = response.json()
            studies = data.get("studies", [])
            print(f"   {city:20s} → {len(studies)} trials found")
    
    print("\n" + "="*70)
    print("✅ All tests complete!")
    print("="*70)
    print("\n💡 Key Findings:")
    print("   - Use 'query.cond' for cancer type")
    print("   - Use 'query.locn' for location (format: 'City, STATE')")
    print("   - Use 'filter.overallStatus=RECRUITING' for active trials")
    print("   - API is working and accessible!")
    print()


if __name__ == "__main__":
    asyncio.run(test_working_api_calls())
