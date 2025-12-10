"""
Test the full chatbot flow with real API integration.
This simulates a complete user conversation.
"""

import httpx
import asyncio
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000"

async def test_full_chatbot_flow():
    """Test complete chatbot conversation with real API"""
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}Testing MaleCare ChatBot - Full Flow with Real API")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Step 1: Start a session with /intake
        print(f"{Fore.YELLOW}Step 1: Starting session with /intake")
        print(f"{Fore.WHITE}POST /intake")
        
        intake_data = {
            "name": "John Smith",
            "gender": "male",
            "cancer_type": "prostate cancer",
            "location": "Boston Massachusetts"
        }
        
        print(f"{Fore.GREEN}Sending intake data:")
        for key, value in intake_data.items():
            print(f"  {key}: {value}")
        
        try:
            response = await client.post(f"{BASE_URL}/intake", json=intake_data)
            response.raise_for_status()
            intake_result = response.json()
            
            session_id = intake_result.get("session_id")
            print(f"\n{Fore.GREEN}✓ Session created!")
            print(f"  Session ID: {session_id}")
            print(f"  Message: {intake_result.get('message')}")
            
        except Exception as e:
            print(f"\n{Fore.RED}✗ Error during intake: {e}")
            return
        
        # Step 2: Get clinical trials (they should auto-display after intake)
        print(f"\n{Fore.YELLOW}Step 2: Checking for clinical trials")
        
        # The trials should be in the intake response
        trials = intake_result.get("trials", [])
        
        if trials:
            print(f"\n{Fore.GREEN}✓ Found {len(trials)} clinical trials!")
            print(f"{Fore.CYAN}{'-'*70}")
            
            for i, trial in enumerate(trials, 1):
                print(f"\n{Fore.CYAN}Trial {i}:")
                print(f"  {Fore.WHITE}NCT ID: {Fore.YELLOW}{trial.get('nct_id')}")
                print(f"  {Fore.WHITE}Title: {trial.get('title')[:60]}...")
                print(f"  {Fore.WHITE}Location: {trial.get('location')}")
                print(f"  {Fore.WHITE}Facility: {trial.get('facility')}")
                print(f"  {Fore.WHITE}Link: {Fore.BLUE}{trial.get('link')}")
                
                # Check if nationwide search
                if trial.get('is_nationwide'):
                    print(f"  {Fore.MAGENTA}(Nationwide result)")
            
            print(f"\n{Fore.CYAN}{'-'*70}")
            
        else:
            print(f"{Fore.YELLOW}No trials in intake response, checking /message endpoint...")
            
            # Try sending a message to get trials
            try:
                message_data = {
                    "session_id": session_id,
                    "message": "show me trials"
                }
                
                response = await client.post(f"{BASE_URL}/message", json=message_data)
                response.raise_for_status()
                message_result = response.json()
                
                print(f"\n{Fore.GREEN}Response: {message_result.get('response')}")
                
                trials = message_result.get("trials", [])
                if trials:
                    print(f"\n{Fore.GREEN}✓ Found {len(trials)} clinical trials!")
                    for i, trial in enumerate(trials, 1):
                        print(f"\n{Fore.CYAN}Trial {i}:")
                        print(f"  NCT ID: {trial.get('nct_id')}")
                        print(f"  Title: {trial.get('title')[:60]}...")
                        print(f"  Link: {Fore.BLUE}{trial.get('link')}")
                
            except Exception as e:
                print(f"{Fore.RED}✗ Error getting trials: {e}")
        
        # Step 3: Test another scenario - small town (triggers nationwide fallback)
        print(f"\n\n{Fore.YELLOW}Step 3: Testing nationwide fallback (small town)")
        print(f"{Fore.WHITE}POST /intake (Siloam Springs, Arkansas)")
        
        intake_data_small_town = {
            "name": "Jane Doe",
            "gender": "female",
            "cancer_type": "lung cancer",
            "location": "Siloam Springs Arkansas"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/intake", json=intake_data_small_town)
            response.raise_for_status()
            intake_result = response.json()
            
            trials = intake_result.get("trials", [])
            
            if trials:
                print(f"\n{Fore.GREEN}✓ Nationwide fallback working!")
                print(f"{Fore.GREEN}Found {len(trials)} trials (nationwide search)")
                
                # Check if trials are marked as nationwide
                nationwide_count = sum(1 for t in trials if t.get('is_nationwide'))
                if nationwide_count > 0:
                    print(f"{Fore.MAGENTA}{nationwide_count} trials marked as nationwide results")
                
                # Show first trial
                if trials:
                    trial = trials[0]
                    print(f"\n{Fore.CYAN}First trial:")
                    print(f"  NCT ID: {trial.get('nct_id')}")
                    print(f"  Title: {trial.get('title')[:60]}...")
                    print(f"  Location: {trial.get('location')}")
                    print(f"  Link: {Fore.BLUE}{trial.get('link')}")
            else:
                print(f"{Fore.RED}✗ No trials returned (fallback may not be working)")
                
        except Exception as e:
            print(f"\n{Fore.RED}✗ Error testing fallback: {e}")
        
        # Summary
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.GREEN}✓ Testing Complete!")
        print(f"{Fore.CYAN}{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(test_full_chatbot_flow())
