"""
Simple test script to verify ClinicalTrials.gov API works
Run this to test the real API before integrating it into the main application

Usage:
    python test_real_api.py
"""

import httpx
import asyncio
import json


async def test_basic_api_call():
    """Test the most basic API call to ClinicalTrials.gov"""
    print("🧪 Testing ClinicalTrials.gov API v2")
    print("=" * 70)
    
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.cond": "breast cancer",
        "filter.overallStatus": "RECRUITING",
        "pageSize": 3,
        "format": "json"
    }
    
    print(f"\n📡 Making API call to: {url}")
    print(f"📋 Parameters: {json.dumps(params, indent=2)}\n")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            print("✅ API call successful!\n")
            print(f"Total trials found: {data.get('totalCount', 0)}")
            print(f"Trials in this response: {len(data.get('studies', []))}\n")
            
            # Display first trial in detail
            studies = data.get("studies", [])
            if studies:
                print("=" * 70)
                print("📄 FIRST TRIAL DETAILS")
                print("=" * 70)
                
                study = studies[0]
                protocol = study.get("protocolSection", {})
                
                # Identification
                identification = protocol.get("identificationModule", {})
                print(f"\n🆔 NCT ID: {identification.get('nctId')}")
                print(f"📋 Title: {identification.get('briefTitle')}")
                
                # Status
                status = protocol.get("statusModule", {})
                print(f"🚦 Status: {status.get('overallStatus')}")
                
                # Phase
                design = protocol.get("designModule", {})
                phases = design.get("phases", [])
                print(f"🔬 Phase: {', '.join(phases) if phases else 'Not specified'}")
                
                # Location
                contacts_locations = protocol.get("contactsLocationsModule", {})
                locations = contacts_locations.get("locations", [])
                if locations:
                    loc = locations[0]
                    print(f"📍 Location: {loc.get('facility')}, {loc.get('city')}, {loc.get('state')}")
                
                # Sponsor
                sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
                lead_sponsor = sponsor_module.get("leadSponsor", {})
                print(f"🏢 Sponsor: {lead_sponsor.get('name')}")
                
                # Link
                nct_id = identification.get('nctId')
                print(f"🔗 Link: https://clinicaltrials.gov/study/{nct_id}")
                
                print("\n" + "=" * 70)
                print("📊 RAW JSON STRUCTURE (first study)")
                print("=" * 70)
                print(json.dumps(study, indent=2)[:2000] + "...")  # First 2000 chars
                
    except httpx.TimeoutException:
        print("❌ Error: Request timed out")
        print("The API might be slow or unreachable")
        
    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print("The API returned an error response")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


async def test_location_search():
    """Test location-based search"""
    print("\n\n🗺️  TESTING LOCATION-BASED SEARCH")
    print("=" * 70)
    
    url = "https://clinicaltrials.gov/api/v2/studies"
    
    # Test different location formats
    test_locations = [
        ("United States:Massachusetts:Boston", "Boston, MA"),
        ("United States:New York:New York", "New York, NY"),
        ("United States:California:Los Angeles", "Los Angeles, CA"),
    ]
    
    for api_location, display_name in test_locations:
        print(f"\n🔍 Searching in: {display_name}")
        print(f"   API format: {api_location}")
        
        params = {
            "query.cond": "cancer",
            "filter.overallStatus": "RECRUITING",
            "filter.geo": api_location,
            "pageSize": 5,
            "format": "json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                total = data.get('totalCount', 0)
                print(f"   ✅ Found {total} trials")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def test_cancer_types():
    """Test different cancer types"""
    print("\n\n🎗️  TESTING DIFFERENT CANCER TYPES")
    print("=" * 70)
    
    url = "https://clinicaltrials.gov/api/v2/studies"
    
    cancer_types = [
        "breast cancer",
        "prostate cancer",
        "lung cancer",
        "colorectal cancer",
        "melanoma"
    ]
    
    for cancer_type in cancer_types:
        params = {
            "query.cond": cancer_type,
            "filter.overallStatus": "RECRUITING",
            "pageSize": 1,
            "format": "json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                total = data.get('totalCount', 0)
                print(f"   {cancer_type:20s} → {total:5d} recruiting trials")
                
        except Exception as e:
            print(f"   {cancer_type:20s} → Error: {e}")


async def main():
    """Run all tests"""
    print("\n🚀 ClinicalTrials.gov API Integration Test Suite")
    print("=" * 70)
    print("This will test if the real API is accessible and working\n")
    
    await test_basic_api_call()
    await test_location_search()
    await test_cancer_types()
    
    print("\n\n✅ TEST COMPLETE!")
    print("=" * 70)
    print("\nIf all tests passed, you're ready to integrate the real API!")
    print("Next step: Replace clinicaltrials_api.py with clinicaltrials_api_REAL.py")


if __name__ == "__main__":
    asyncio.run(main())
