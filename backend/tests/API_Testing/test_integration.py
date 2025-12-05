"""
Test the updated clinicaltrials_api.py with real API integration
This tests the functions directly without needing the full server running
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path so we can import app modules
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.clinicaltrials_api import search_clinical_trials


async def test_real_api_integration():
    """Test the real API integration"""
    
    print("\n" + "="*70)
    print("🧪 Testing Real ClinicalTrials.gov API Integration")
    print("="*70 + "\n")
    
    # Test cases matching our chatbot use cases
    test_cases = [
        ("breast cancer", "Boston Massachusetts"),
        ("prostate cancer", "New York New York"),
        ("lung cancer", "Los Angeles California"),
    ]
    
    for cancer_type, location in test_cases:
        print(f"\n🔍 Searching: {cancer_type} in {location}")
        print("-" * 70)
        
        try:
            trials = await search_clinical_trials(cancer_type, location)
            
            if trials:
                print(f"✅ Found {len(trials)} trials\n")
                
                # Show first 3 trials
                for i, trial in enumerate(trials[:3], 1):
                    print(f"{i}. NCT ID: {trial['nct_id']}")
                    print(f"   Title: {trial['title'][:70]}...")
                    print(f"   Phase: {trial['phase']}")
                    print(f"   Status: {trial['status']}")
                    print(f"   Facility: {trial['facility']}")
                    print(f"   Sponsor: {trial['sponsor']}")
                    print(f"   Link: {trial['link']}")
                    print()
                
                # Check if we got real data (not mock)
                first_nct = trials[0]['nct_id']
                if first_nct == "NCT12345678":
                    print("⚠️  WARNING: Still getting mock data!")
                elif first_nct == "API_ERROR":
                    print("⚠️  WARNING: API error occurred")
                else:
                    print(f"✅ SUCCESS: Real API data! (NCT ID: {first_nct})")
            else:
                print("❌ No trials found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ Test Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_real_api_integration())
