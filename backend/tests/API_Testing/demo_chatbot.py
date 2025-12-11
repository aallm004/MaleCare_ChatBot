"""
Quick Demo - Shows the interactive chatbot in action
This simulates user input to demonstrate the automatic trial display
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
    """Run a demo showing the automatic trial display"""
    
    print("\n" + "="*70)
    print(f"{Colors.BOLD}{Colors.OKBLUE}🏥 MaleCare ChatBot - Quick Demo{Colors.ENDC}")
    print("="*70 + "\n")
    
    # Demo inputs
    demos = [
        {
            "name": "Sarah",
            "gender": "female",
            "cancer": "breast cancer",
            "location": "Boston Massachusetts"
        },
        {
            "name": "Michael",
            "gender": "male",
            "cancer": "prostate cancer",
            "location": "New York New York"
        },
        {
            "name": "Jennifer",
            "gender": "female",
            "cancer": "lung cancer",
            "location": "Los Angeles California"
        }
    ]
    
    for demo_data in demos:
        print(f"\n{Colors.BOLD}Demo: {demo_data['name']} searching for {demo_data['cancer']}{Colors.ENDC}")
        print("-" * 70 + "\n")
        
        # Show intake
        print(f"{Colors.OKGREEN}Name:{Colors.ENDC} {demo_data['name']}")
        print(f"{Colors.OKGREEN}Gender:{Colors.ENDC} {demo_data['gender']}")
        print(f"{Colors.OKGREEN}Cancer Type:{Colors.ENDC} {demo_data['cancer']}")
        print(f"{Colors.OKGREEN}Location:{Colors.ENDC} {demo_data['location']}")
        print()
        
        # Search
        print(f"{Colors.WARNING}🔍 Searching ClinicalTrials.gov...{Colors.ENDC}\n")
        
        trials = await search_clinical_trials(
            cancer_type=demo_data['cancer'],
            location=demo_data['location']
        )
        
        if trials and trials[0].get('nct_id') != 'API_ERROR':
            print(f"{Colors.BOLD}{Colors.OKGREEN}✅ Found {len(trials)} trials!{Colors.ENDC}\n")
            
            # Show first 3 trials
            for i, trial in enumerate(trials[:3], 1):
                print(f"{Colors.BOLD}Trial {i}:{Colors.ENDC}")
                print(f"  {Colors.OKBLUE}NCT ID:{Colors.ENDC} {trial['nct_id']}")
                print(f"  {Colors.BOLD}Title:{Colors.ENDC} {trial['title'][:70]}...")
                print(f"  Phase: {trial['phase']}")
                print(f"  Facility: {trial['facility']}")
                
                # Clickable link
                link = trial['link']
                print(f"  {Colors.UNDERLINE}{Colors.OKBLUE}🔗 Link:{Colors.ENDC} {link}")
                print()
            
            if len(trials) > 3:
                print(f"  ... and {len(trials) - 3} more trials")
                print()
        else:
            print(f"{Colors.WARNING}No trials found for this search{Colors.ENDC}\n")
        
        print("=" * 70)
        
        # Pause between demos
        await asyncio.sleep(1)
    
    print(f"\n{Colors.BOLD}Demo complete! This is how the chatbot works:{Colors.ENDC}")
    print("1. User enters name, gender, cancer type, and location")
    print("2. Chatbot AUTOMATICALLY searches ClinicalTrials.gov")
    print("3. Real trials appear with clickable links")
    print("4. User can click links to learn more or restart for new search\n")
    print(f"{Colors.OKGREEN}To try it yourself, run: python interactive_test_real_api.py{Colors.ENDC}\n")


if __name__ == "__main__":
    asyncio.run(demo())
