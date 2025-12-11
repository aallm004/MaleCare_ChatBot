"""
Interactive Chatbot Tester
Run this script to manually test the chatbot via command line
"""
import httpx
import asyncio
import json
from typing import Optional

# API Base URL
BASE_URL = "http://localhost:8000"

class ChatbotTester:
    def __init__(self, user_id: str = "interactive_test_user"):
        self.user_id = user_id
        self.client = httpx.AsyncClient()
        
    async def submit_intake(self, 
                           cancer_type: str,
                           stage: str,
                           age: int,
                           sex: str,
                           location: str,
                           comorbidities: Optional[list] = None,
                           prior_treatments: Optional[list] = None):
        """Submit intake form"""
        data = {
            "user_id": self.user_id,
            "cancer_type": cancer_type,
            "stage": stage,
            "age": age,
            "sex": sex,
            "location": location,
            "comorbidities": comorbidities or [],
            "prior_treatments": prior_treatments or []
        }
        
        response = await self.client.post(f"{BASE_URL}/intake", json=data)
        result = response.json()
        print(f"\n🤖 Bot: {result['response']}\n")
        return result
        
    async def send_message(self, message: str):
        """Send a message to the chatbot"""
        data = {
            "user_id": self.user_id,
            "message": message
        }
        
        response = await self.client.post(f"{BASE_URL}/message", json=data)
        result = response.json()
        
        print(f"\n🤖 Bot: {result.get('response', 'No response')}")
        
        if "trials" in result:
            print(f"\n📋 Found {len(result['trials'])} clinical trial(s):")
            for i, trial in enumerate(result['trials'], 1):
                print(f"\n   {i}. {trial.get('title', 'No title')}")
                print(f"      Phase: {trial.get('phase', 'N/A')}")
                print(f"      Status: {trial.get('status', 'N/A')}")
                print(f"      Location: {trial.get('location', 'N/A')}")
                print(f"      Link: {trial.get('link', 'N/A')}")
        print()
        return result
        
    async def end_session(self):
        """End the chat session"""
        data = {"user_id": self.user_id}
        response = await self.client.post(f"{BASE_URL}/end-session", json=data)
        print("\n✓ Session ended\n")
        await self.client.aclose()


async def main():
    """Main interactive test function"""
    print("\n" + "="*70)
    print(" 🏥 MaleCare Clinical Trials Chatbot - Interactive Tester")
    print("="*70)
    
    print("\nMake sure the backend is running: uvicorn app.main:app --reload")
    print("Press Ctrl+C to exit at any time\n")
    
    # Test server connection
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code != 200:
                print("❌ Backend server is not responding. Please start it first.")
                return
            print("✓ Backend server is running\n")
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("   Please start the server with: uvicorn app.main:app --reload")
        return
    
    tester = ChatbotTester()
    
    try:
        # Step 1: Collect intake information
        print("-" * 70)
        print("STEP 1: Patient Intake Form")
        print("-" * 70)
        
        cancer_type = input("Cancer type (e.g., breast cancer, prostate cancer): ").strip()
        stage = input("Stage (e.g., stage 1, stage 2): ").strip()
        age = int(input("Age: ").strip())
        sex = input("Sex (male/female): ").strip()
        location = input("Location (e.g., California, New York): ").strip()
        
        comorbidities_input = input("Comorbidities (comma-separated, or press Enter to skip): ").strip()
        comorbidities = [c.strip() for c in comorbidities_input.split(",")] if comorbidities_input else []
        
        treatments_input = input("Prior treatments (comma-separated, or press Enter to skip): ").strip()
        prior_treatments = [t.strip() for t in treatments_input.split(",")] if treatments_input else []
        
        # Submit intake
        await tester.submit_intake(
            cancer_type=cancer_type,
            stage=stage,
            age=age,
            sex=sex,
            location=location,
            comorbidities=comorbidities,
            prior_treatments=prior_treatments
        )
        
        # Step 2: Chat loop
        print("-" * 70)
        print("STEP 2: Chat with the Bot")
        print("-" * 70)
        print("Type your messages below. Type 'quit' or 'exit' to end.\n")
        
        while True:
            user_input = input("💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if not user_input:
                continue
                
            await tester.send_message(user_input)
        
        # End session
        await tester.end_session()
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        await tester.end_session()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        await tester.client.aclose()
    
    print("\n" + "="*70)
    print(" Thank you for testing the MaleCare Chatbot!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
