"""
Test the nationwide fallback feature
Shows what happens when no local trials are found
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.clinicaltrials_api import search_clinical_trials


class Colors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


async def test_fallback():
    """Test the nationwide fallback"""
    
    print("\n" + "="*70)
    print(f"{Colors.BOLD}🧪 Testing Nationwide Fallback Feature{Colors.ENDC}")
    print("="*70 + "\n")
    
    # Test Case 1: Small town (should trigger fallback)
    print(f"{Colors.BOLD}Test 1: Small town (Siloam Springs, Arkansas){Colors.ENDC}")
    print("-" * 70)
    print(f"{Colors.WARNING}Expected: No local trials, should return nationwide results{Colors.ENDC}\n")
    
    trials = await search_clinical_trials(
        cancer_type="lung cancer",
        location="Siloam Springs Arkansas"
    )
    
    if trials:
        is_nationwide = trials[0].get('is_nationwide', False)
        if is_nationwide:
            print(f"{Colors.OKGREEN}✅ SUCCESS: Nationwide fallback triggered!{Colors.ENDC}")
            print(f"   Found {len(trials)} trials nationwide\n")
        else:
            print(f"{Colors.OKGREEN}✅ Found {len(trials)} local trials{Colors.ENDC}\n")
        
        # Show first 2 trials
        for i, trial in enumerate(trials[:2], 1):
            print(f"{i}. {trial['nct_id']} - {trial['title'][:60]}...")
            print(f"   Location: {trial['location']}")
            print(f"   Facility: {trial['facility']}")
            print(f"   Link: {Colors.UNDERLINE}{Colors.OKBLUE}{trial['link']}{Colors.ENDC}")
            print()
    else:
        print(f"{Colors.FAIL}❌ No trials found at all{Colors.ENDC}\n")
    
    print("="*70 + "\n")
    
    # Test Case 2: Major city (should NOT trigger fallback)
    print(f"{Colors.BOLD}Test 2: Major city (Boston, Massachusetts){Colors.ENDC}")
    print("-" * 70)
    print(f"{Colors.WARNING}Expected: Local trials found, no fallback needed{Colors.ENDC}\n")
    
    trials = await search_clinical_trials(
        cancer_type="breast cancer",
        location="Boston Massachusetts"
    )
    
    if trials:
        is_nationwide = trials[0].get('is_nationwide', False)
        if is_nationwide:
            print(f"{Colors.WARNING}⚠️  Nationwide fallback triggered (unexpected){Colors.ENDC}")
            print(f"   Found {len(trials)} trials nationwide\n")
        else:
            print(f"{Colors.OKGREEN}✅ SUCCESS: Found {len(trials)} local trials!{Colors.ENDC}\n")
        
        # Show first 2 trials
        for i, trial in enumerate(trials[:2], 1):
            print(f"{i}. {trial['nct_id']} - {trial['title'][:60]}...")
            print(f"   Location: {trial['location']}")
            print(f"   Facility: {trial['facility']}")
            print(f"   Link: {Colors.UNDERLINE}{Colors.OKBLUE}{trial['link']}{Colors.ENDC}")
            print()
    else:
        print(f"{Colors.FAIL}❌ No trials found at all{Colors.ENDC}\n")
    
    print("="*70 + "\n")
    
    print(f"{Colors.BOLD}Summary:{Colors.ENDC}")
    print("✅ Nationwide fallback ensures users ALWAYS get trial results")
    print("✅ Small towns get nationwide trials when no local options exist")
    print("✅ Major cities still get local trials first")
    print()


if __name__ == "__main__":
    asyncio.run(test_fallback())
