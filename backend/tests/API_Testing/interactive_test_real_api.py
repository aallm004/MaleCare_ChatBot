"""
Interactive Console Chatbot Tester with Real API
Test the MaleCare ChatBot with real ClinicalTrials.gov data!

Usage:
    python interactive_test_real_api.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.services.clinicaltrials_api import search_clinical_trials
from app.services.nlp import predict_intent, predict_entities
from app.core.state import active_states


class Colors:
    """ANSI color codes for pretty output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header():
    """Print chatbot header"""
    print("\n" + "="*70)
    print(f"{Colors.BOLD}{Colors.OKBLUE}🏥 MaleCare Clinical Trials ChatBot (Real API){Colors.ENDC}")
    print("="*70 + "\n")
    print("Now using REAL ClinicalTrials.gov data! 🎉")
    print("Trials will appear automatically after you provide your info.\n")
    print("Commands:")
    print("  - Type your message to continue chatting")
    print("  - Type 'restart' to search for different trials")
    print("  - Type 'quit' or 'exit' to end")
    print("\n" + "="*70 + "\n")


def print_bot_message(message: str):
    """Print bot message in color"""
    print(f"{Colors.OKCYAN}🤖 ChatBot:{Colors.ENDC} {message}\n")


def print_user_message(message: str):
    """Print user message in color"""
    print(f"{Colors.OKGREEN}👤 You:{Colors.ENDC} {message}\n")


def print_trial(trial: dict, index: int):
    """Print a single trial with clickable link"""
    print(f"{Colors.BOLD}Trial {index}:{Colors.ENDC}")
    print(f"  {Colors.OKBLUE}NCT ID:{Colors.ENDC} {trial['nct_id']}")
    print(f"  {Colors.BOLD}Title:{Colors.ENDC} {trial['title']}")
    print(f"  Phase: {trial['phase']}")
    print(f"  Status: {trial['status']}")
    print(f"  Facility: {trial['facility']}")
    print(f"  Sponsor: {trial['sponsor']}")
    
    # Print clickable link (works in most modern terminals)
    link = trial['link']
    print(f"  {Colors.UNDERLINE}{Colors.OKBLUE}🔗 Link:{Colors.ENDC} {link}")
    print()


async def handle_intake(user_id: str):
    """Handle intake process - gather all info at once"""
    print_bot_message("Welcome! I'm here to help you find clinical trials.")
    print_bot_message("Please provide the following information (one per line):\n")
    
    # Collect patient info all at once
    print(f"{Colors.BOLD}1. Name:{Colors.ENDC}")
    name = input(f"   {Colors.OKGREEN}>{Colors.ENDC} ").strip()
    
    print(f"\n{Colors.BOLD}2. Gender:{Colors.ENDC} {Colors.WARNING}(male/female){Colors.ENDC}")
    sex = input(f"   {Colors.OKGREEN}>{Colors.ENDC} ").strip()
    
    print(f"\n{Colors.BOLD}3. Cancer Type:{Colors.ENDC} {Colors.WARNING}(e.g., breast cancer, prostate cancer, lung cancer){Colors.ENDC}")
    cancer_type = input(f"   {Colors.OKGREEN}>{Colors.ENDC} ").strip()
    
    print(f"\n{Colors.BOLD}4. Location:{Colors.ENDC} {Colors.WARNING}(City State, e.g., Boston Massachusetts){Colors.ENDC}")
    location = input(f"   {Colors.OKGREEN}>{Colors.ENDC} ").strip()
    
    print()
    
    # Store state
    active_states[user_id] = {
        "name": name,
        "cancer_type": cancer_type,
        "sex": sex,
        "location": location,
        "intake_complete": True
    }
    
    print_bot_message(f"Perfect! Here's what I have:")
    print(f"  👤 Name: {Colors.BOLD}{name}{Colors.ENDC}")
    print(f"  ⚧ Gender: {sex}")
    print(f"  🎗️  Cancer Type: {Colors.BOLD}{cancer_type}{Colors.ENDC}")
    print(f"  📍 Location: {location}")
    print()
    
    # Automatically search for trials!
    print_bot_message(f"Great! Now let me search for {Colors.BOLD}{cancer_type}{Colors.ENDC} trials in {Colors.BOLD}{location}{Colors.ENDC}...")
    print(f"{Colors.WARNING}⏳ Calling ClinicalTrials.gov API... (this may take 1-3 seconds){Colors.ENDC}\n")
    
    start_time = datetime.now()
    
    # Search for real trials!
    trials = await search_clinical_trials(
        cancer_type=cancer_type,
        location=location
    )
    
    end_time = datetime.now()
    response_time = (end_time - start_time).total_seconds()
    
    print(f"{Colors.WARNING}✅ API responded in {response_time:.2f} seconds{Colors.ENDC}\n")
    
    if trials and trials[0].get('nct_id') != 'API_ERROR':
        # Check if these are nationwide results
        is_nationwide = trials[0].get('is_nationwide', False)
        
        if is_nationwide:
            print_bot_message(f"I didn't find trials specifically in {location}, but I found {Colors.BOLD}{len(trials)}{Colors.ENDC} recruiting trials nationwide for {name}:\n")
            print(f"{Colors.WARNING}💡 These trials may be in different locations, but they're actively recruiting!{Colors.ENDC}\n")
        else:
            print_bot_message(f"Excellent news, {name}! I found {Colors.BOLD}{len(trials)}{Colors.ENDC} recruiting clinical trials for you:\n")
        
        for i, trial in enumerate(trials, 1):
            print_trial(trial, i)
        
        print_bot_message(f"Found {len(trials)} trials total. Click the links above to learn more!")
        print(f"\n{Colors.WARNING}💡 Tip: You can ctrl+click or cmd+click the blue links to open them in your browser!{Colors.ENDC}\n")
        
    elif trials and trials[0].get('nct_id') == 'API_ERROR':
        print_bot_message(f"I'm having trouble connecting to ClinicalTrials.gov right now. Please try again in a moment.")
        print(f"{Colors.FAIL}Error: {trials[0].get('message', 'Unknown error')}{Colors.ENDC}\n")
        
    else:
        print_bot_message(f"I couldn't find any recruiting trials for {cancer_type} in {location}.")
        print_bot_message("You might want to:")
        print("  - Try a different location")
        print("  - Visit ClinicalTrials.gov directly")
        print(f"  - Contact your healthcare provider for alternatives\n")
    
    print_bot_message("You can continue chatting or type 'restart' for a new search, 'quit' to exit.")
    print()


async def handle_message(user_id: str, message: str):
    """Handle user message and search for trials"""
    
    # Check if intake is complete
    if user_id not in active_states or not active_states[user_id].get("intake_complete"):
        print_bot_message("I need to collect your information first. Let me restart the intake process.")
        await handle_intake(user_id)
        return
    
    state = active_states[user_id]
    
    # Predict intent
    intent = predict_intent(message)
    print(f"{Colors.WARNING}[Debug] Detected intent: {intent}{Colors.ENDC}\n")
    
    if intent == "greeting":
        print_bot_message(f"Hello {state.get('name', 'there')}! I'm ready to help you find clinical trials. Just ask me to show you trials!")
        
    elif intent == "find_trials":
        print_bot_message(f"Searching for {Colors.BOLD}{state['cancer_type']}{Colors.ENDC} trials in {Colors.BOLD}{state['location']}{Colors.ENDC}...")
        print(f"{Colors.WARNING}⏳ Calling ClinicalTrials.gov API... (this may take 1-3 seconds){Colors.ENDC}\n")
        
        start_time = datetime.now()
        
        # Search for real trials!
        trials = await search_clinical_trials(
            cancer_type=state['cancer_type'],
            location=state['location']
        )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        print(f"{Colors.WARNING}✅ API responded in {response_time:.2f} seconds{Colors.ENDC}\n")
        
        if trials and trials[0].get('nct_id') != 'API_ERROR':
            # Check if these are nationwide results
            is_nationwide = trials[0].get('is_nationwide', False)
            
            if is_nationwide:
                print_bot_message(f"I didn't find trials in {state['location']}, but I found {Colors.BOLD}{len(trials)}{Colors.ENDC} recruiting trials nationwide:\n")
                print(f"{Colors.WARNING}💡 These trials may be in different locations, but they're actively recruiting!{Colors.ENDC}\n")
            else:
                print_bot_message(f"Great news, {state.get('name', '')}! I found {Colors.BOLD}{len(trials)}{Colors.ENDC} recruiting clinical trials for you:\n")
            
            for i, trial in enumerate(trials, 1):
                print_trial(trial, i)
            
            print_bot_message(f"Found {len(trials)} trials total. Click the links above to learn more!")
            print(f"\n{Colors.WARNING}💡 Tip: You can ctrl+click or cmd+click the blue links to open them in your browser!{Colors.ENDC}\n")
            
        elif trials and trials[0].get('nct_id') == 'API_ERROR':
            print_bot_message(f"I'm having trouble connecting to ClinicalTrials.gov right now. Please try again in a moment.")
            print(f"{Colors.FAIL}Error: {trials[0].get('message', 'Unknown error')}{Colors.ENDC}\n")
            
        else:
            print_bot_message(f"I couldn't find any recruiting trials for {state['cancer_type']} in {state['location']}.")
            print_bot_message("You might want to:")
            print("  - Try a different location")
            print("  - Visit ClinicalTrials.gov directly")
            print(f"  - Contact your healthcare provider for alternatives\n")
    
    elif intent == "goodbye":
        print_bot_message(f"Thank you for using the MaleCare ChatBot, {state.get('name', '')}! Take care and best wishes on your journey. 💙")
        return "END"
    
    else:
        print_bot_message("I didn't quite understand that. You can ask me to:")
        print("  - 'Show me clinical trials'")
        print("  - 'Find trials'")
        print("  - 'What trials are available?'")
        print()


async def main():
    """Main interactive loop"""
    print_header()
    
    user_id = "interactive_user"
    
    # Start with intake
    await handle_intake(user_id)
    
    # Chat loop
    while True:
        try:
            user_input = input(f"{Colors.OKGREEN}👤 You:{Colors.ENDC} ").strip()
            print()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print_bot_message("Goodbye! 👋")
                break
            
            if user_input.lower() == 'restart':
                print_bot_message("Starting a new session...\n")
                if user_id in active_states:
                    del active_states[user_id]
                await handle_intake(user_id)
                continue
            
            result = await handle_message(user_id, user_input)
            
            if result == "END":
                break
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
            break
        except Exception as e:
            print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}\n")
            import traceback
            traceback.print_exc()
    
    print(f"\n{Colors.OKBLUE}Thank you for testing the MaleCare ChatBot!{Colors.ENDC}\n")


if __name__ == "__main__":
    asyncio.run(main())
