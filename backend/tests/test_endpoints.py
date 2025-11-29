"""
Test suite for chatbot endpoints
"""
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

# Test Health Endpoint
def test_health():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# Test Intake Form Submission
def test_intake_submission():
    """Test submitting patient intake form"""
    intake_data = {
        "user_id": "test_user_123",
        "cancer_type": "breast cancer",
        "stage": "stage 2",
        "age": 45,
        "sex": "female",
        "location": "California",
        "comorbidities": ["diabetes"],
        "prior_treatments": ["chemotherapy"]
    }
    
    response = client.post("/intake", json=intake_data)
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert body["intake_complete"] == True
    print(f"\n✓ Intake response: {body['response']}")


# Test Message Without Intake (Should Fail)
def test_message_without_intake():
    """Test sending message before completing intake form"""
    response = client.post("/message", json={
        "user_id": "new_user_456",
        "message": "Find me trials"
    })
    assert response.status_code == 200
    body = response.json()
    assert "requires_intake" in body or "intake" in body["response"].lower()
    print(f"\n✓ Blocked message: {body['response']}")


# Test Greeting Intent
def test_greeting_intent():
    """Test that bot recognizes greeting"""
    # First submit intake
    client.post("/intake", json={
        "user_id": "test_user_greeting",
        "cancer_type": "prostate cancer",
        "stage": "stage 1",
        "age": 60,
        "sex": "male",
        "location": "New York"
    })
    
    # Then send greeting
    response = client.post("/message", json={
        "user_id": "test_user_greeting",
        "message": "Hello!"
    })
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    print(f"\n✓ Greeting response: {body['response']}")


# Test Find Trials Intent
def test_find_trials_intent():
    """Test finding clinical trials"""
    # Submit intake first
    client.post("/intake", json={
        "user_id": "test_user_trials",
        "cancer_type": "lung cancer",
        "stage": "stage 3",
        "age": 55,
        "sex": "male",
        "location": "Texas"
    })
    
    # Request trials
    response = client.post("/message", json={
        "user_id": "test_user_trials",
        "message": "Can you find clinical trials for me?"
    })
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    print(f"\n✓ Trials response: {body['response']}")
    if "trials" in body:
        print(f"  Found {len(body['trials'])} trials")
        for trial in body['trials']:
            print(f"    - {trial.get('title', 'No title')}")


# Test Goodbye Intent
def test_goodbye_intent():
    """Test that bot recognizes goodbye"""
    # Submit intake first
    client.post("/intake", json={
        "user_id": "test_user_goodbye",
        "cancer_type": "breast cancer",
        "stage": "stage 2",
        "age": 50,
        "sex": "female",
        "location": "Florida"
    })
    
    # Say goodbye
    response = client.post("/message", json={
        "user_id": "test_user_goodbye",
        "message": "Thanks, goodbye!"
    })
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    print(f"\n✓ Goodbye response: {body['response']}")


# Test End Session
def test_end_session():
    """Test ending a user session"""
    # Create a session first
    client.post("/intake", json={
        "user_id": "test_user_session",
        "cancer_type": "colon cancer",
        "stage": "stage 2",
        "age": 65,
        "sex": "male",
        "location": "Ohio"
    })
    
    # End the session
    response = client.post("/end-session", json={
        "user_id": "test_user_session"
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "session_cleared"
    print(f"\n✓ Session ended successfully")


# Test Full Conversation Flow
def test_full_conversation_flow():
    """Test a complete conversation from start to finish"""
    user_id = "test_user_full_flow"
    
    print("\n" + "="*60)
    print("FULL CONVERSATION FLOW TEST")
    print("="*60)
    
    # Step 1: Submit intake
    print("\n1. Submitting intake form...")
    intake_response = client.post("/intake", json={
        "user_id": user_id,
        "cancer_type": "breast cancer",
        "stage": "stage 2",
        "age": 48,
        "sex": "female",
        "location": "California",
        "comorbidities": ["hypertension"],
        "prior_treatments": ["surgery"]
    })
    assert intake_response.status_code == 200
    print(f"   Bot: {intake_response.json()['response']}")
    
    # Step 2: Greeting
    print("\n2. Saying hello...")
    greeting_response = client.post("/message", json={
        "user_id": user_id,
        "message": "Hi there!"
    })
    assert greeting_response.status_code == 200
    print(f"   Bot: {greeting_response.json()['response']}")
    
    # Step 3: Ask for trials
    print("\n3. Asking for clinical trials...")
    trials_response = client.post("/message", json={
        "user_id": user_id,
        "message": "I'm looking for clinical trials in Los Angeles"
    })
    assert trials_response.status_code == 200
    trials_data = trials_response.json()
    print(f"   Bot: {trials_data['response']}")
    if "trials" in trials_data:
        print(f"   Found {len(trials_data['trials'])} trials")
    
    # Step 4: Say goodbye
    print("\n4. Ending conversation...")
    goodbye_response = client.post("/message", json={
        "user_id": user_id,
        "message": "Thank you, goodbye!"
    })
    assert goodbye_response.status_code == 200
    print(f"   Bot: {goodbye_response.json()['response']}")
    
    # Step 5: End session
    print("\n5. Clearing session...")
    session_response = client.post("/end-session", json={
        "user_id": user_id
    })
    assert session_response.status_code == 200
    print("   ✓ Session cleared")
    
    print("\n" + "="*60)
    print("CONVERSATION FLOW COMPLETE")
    print("="*60)