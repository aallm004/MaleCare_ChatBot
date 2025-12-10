"""
Demo showing the nationwide fallback in action
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
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


async def demo():
    """Demo the nationwide fallback"""
    
    print("\n" + "="*70)
    print(f"{Colors.BOLD}{Colors.OKBLUE}🏥 Nationwide Fallback Demo{Colors.ENDC}")
    print("="*70 + "\n")
    
    print(f"{Colors.BOLD}Scenario: User from a small town{Colors.ENDC}")
    print("Name: James")
    print("Gender: male")
    print("Cancer Type: lung cancer")
    print("Location: Siloam Springs Arkansas (small town)")
    print()
    
    print(f"{Colors.WARNING}🔍 Searching for local trials first...{Colors.ENDC}\n")
    
    trials = await search_clinical_trials(
        cancer_type="lung cancer",
        location="Siloam Springs Arkansas"
    )
    
    is_nationwide = trials[0].get('is_nationwide', False) if trials else False
    
    if is_nationwide:
        print(f"{Colors.OKGREEN}💡 No local trials found, but don't worry!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}   We automatically searched nationwide and found {len(trials)} trials!{Colors.ENDC}\n")
    else:
        print(f"{Colors.OKGREEN}✅ Found {len(trials)} trials locally!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Results:{Colors.ENDC}\n")
    
    for i, trial in enumerate(trials[:3], 1):
        print(f"{Colors.BOLD}Trial {i}:{Colors.ENDC}")
        print(f"  NCT ID: {trial['nct_id']}")
        print(f"  Title: {trial['title'][:65]}...")
        print(f"  Location: {Colors.WARNING}{trial['location']}{Colors.ENDC}")
        print(f"  Facility: {trial['facility']}")
        print(f"  {Colors.UNDERLINE}{Colors.OKBLUE}Link: {trial['link']}{Colors.ENDC}")
        print()
    
    if len(trials) > 3:
        print(f"  ... and {len(trials) - 3} more trials available!\n")
    
    print("="*70)
    print(f"\n{Colors.BOLD}Key Feature:{Colors.ENDC}")
    print("✅ Users from ANY location will always get trial results")
    print("✅ Small towns automatically get nationwide options")
    print("✅ No more 'no trials found' dead ends")
    print("✅ Trials show their actual locations so users can decide")
    print()


if __name__ == "__main__":
    asyncio.run(demo())
