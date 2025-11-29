"""
Automated API Performance Testing Script

Runs API tests every 30 minutes for 1 week, testing:
- Different cancer types (breast, prostate, lung)
- Random patient data
- Response times
- Error handling

Results are saved to CSV files for analysis.
"""

import asyncio
import httpx
import random
import time
import csv
from datetime import datetime, timedelta
from pathlib import Path
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_DURATION_DAYS = 7
TEST_INTERVAL_MINUTES = 30
RESULTS_DIR = Path(__file__).parent / "test_results"

# Test data pools
CANCER_TYPES = ["breast cancer", "prostate cancer", "lung cancer"]
STAGES = ["stage 1", "stage 2", "stage 3", "stage 4"]
LOCATIONS = [
    "Phoenix Arizona",
    "Los Angeles California",
    "New York New York",
    "Houston Texas",
    "Chicago Illinois",
    "Miami Florida",
    "Seattle Washington",
    "Boston Massachusetts",
    "Denver Colorado",
    "Atlanta Georgia"
]
FIRST_NAMES_FEMALE = ["Emma", "Olivia", "Sophia", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn", "Abigail"]
FIRST_NAMES_MALE = ["Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan"]
COMORBIDITIES_POOL = ["diabetes", "hypertension", "heart disease", "asthma", "arthritis"]
TREATMENTS_POOL = ["chemotherapy", "radiation", "surgery", "immunotherapy", "hormone therapy"]


def generate_random_patient():
    """Generate random patient data for testing."""
    # Select cancer type
    cancer_type = random.choice(CANCER_TYPES)
    
    # Set sex based on cancer type probabilities
    if cancer_type == "breast cancer":
        sex = "female" if random.random() < 0.99 else "male"  # 99% female for breast cancer
    elif cancer_type == "prostate cancer":
        sex = "male"  # 100% male for prostate cancer
    else:  # lung cancer
        sex = random.choice(["male", "female"])
    
    # Select appropriate first name
    if sex == "female":
        first_name = random.choice(FIRST_NAMES_FEMALE)
    else:
        first_name = random.choice(FIRST_NAMES_MALE)
    
    # Generate user_id from name
    user_id = f"{first_name.lower()}_{random.randint(100, 999)}"
    
    # Generate age (appropriate range for cancer patients)
    if cancer_type == "prostate cancer":
        age = random.randint(50, 80)  # Prostate cancer more common in older men
    elif cancer_type == "breast cancer":
        age = random.randint(40, 75)  # Breast cancer peaks in middle age
    else:  # lung cancer
        age = random.randint(45, 80)  # Lung cancer typically older patients
    
    # Random comorbidities (0-3)
    num_comorbidities = random.randint(0, 3)
    comorbidities = random.sample(COMORBIDITIES_POOL, num_comorbidities) if num_comorbidities > 0 else []
    
    # Random prior treatments (0-2)
    num_treatments = random.randint(0, 2)
    prior_treatments = random.sample(TREATMENTS_POOL, num_treatments) if num_treatments > 0 else []
    
    return {
        "user_id": user_id,
        "cancer_type": cancer_type,
        "stage": random.choice(STAGES),
        "age": age,
        "sex": sex,
        "location": random.choice(LOCATIONS),
        "comorbidities": comorbidities,
        "prior_treatments": prior_treatments
    }


async def test_api_endpoint(patient_data):
    """Test the API with given patient data and record metrics."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "user_id": patient_data["user_id"],
        "cancer_type": patient_data["cancer_type"],
        "stage": patient_data["stage"],
        "age": patient_data["age"],
        "sex": patient_data["sex"],
        "location": patient_data["location"],
        "intake_response_time": None,
        "intake_status": None,
        "intake_error": None,
        "message_response_time": None,
        "message_status": None,
        "message_error": None,
        "trials_found": 0,
        "total_response_time": None,
        "success": False
    }
    
    total_start = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test 1: Submit intake form
            intake_start = time.time()
            try:
                intake_response = await client.post(
                    f"{API_BASE_URL}/intake",
                    json=patient_data
                )
                intake_time = time.time() - intake_start
                results["intake_response_time"] = round(intake_time, 6)
                results["intake_status"] = intake_response.status_code
                
                if intake_response.status_code != 200:
                    results["intake_error"] = f"Status {intake_response.status_code}"
                    return results
                    
            except Exception as e:
                results["intake_error"] = str(e)
                results["intake_response_time"] = time.time() - intake_start
                return results
            
            # Test 2: Send message to find trials
            message_start = time.time()
            try:
                message_response = await client.post(
                    f"{API_BASE_URL}/message",
                    json={
                        "user_id": patient_data["user_id"],
                        "message": "Find me clinical trials"
                    }
                )
                message_time = time.time() - message_start
                results["message_response_time"] = round(message_time, 6)
                results["message_status"] = message_response.status_code
                
                if message_response.status_code == 200:
                    response_data = message_response.json()
                    if "trials" in response_data:
                        results["trials_found"] = len(response_data["trials"])
                    results["success"] = True
                else:
                    results["message_error"] = f"Status {message_response.status_code}"
                    
            except Exception as e:
                results["message_error"] = str(e)
                results["message_response_time"] = time.time() - message_start
                return results
            
            # Clean up: End session
            try:
                await client.post(
                    f"{API_BASE_URL}/end-session",
                    json={"user_id": patient_data["user_id"]}
                )
            except:
                pass  # Don't fail the test if cleanup fails
                
    except Exception as e:
        results["intake_error"] = f"Connection error: {str(e)}"
    
    results["total_response_time"] = round(time.time() - total_start, 6)
    return results


def save_results_to_csv(results, filename="api_test_results.csv"):
    """Save test results to CSV file."""
    RESULTS_DIR.mkdir(exist_ok=True)
    filepath = RESULTS_DIR / filename
    
    # Check if file exists to determine if we need headers
    file_exists = filepath.exists()
    
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results.keys())
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(results)
    
    print(f"✓ Results saved to {filepath}")


def print_results(results):
    """Print formatted test results."""
    print("\n" + "="*70)
    print(f"Test Run: {results['timestamp']}")
    print("="*70)
    print(f"Patient: {results['user_id']}")
    print(f"Cancer Type: {results['cancer_type']}")
    print(f"Stage: {results['stage']}")
    print(f"Age: {results['age']} | Sex: {results['sex']}")
    print(f"Location: {results['location']}")
    print("-"*70)
    
    if results['intake_error']:
        print(f"❌ Intake Error: {results['intake_error']}")
    else:
        print(f"✓ Intake Response Time: {results['intake_response_time']:.6f} seconds")
    
    if results['message_error']:
        print(f"❌ Message Error: {results['message_error']}")
    else:
        print(f"✓ Message Response Time: {results['message_response_time']:.6f} seconds")
        print(f"✓ Trials Found: {results['trials_found']}")
    
    print(f"\n📊 Total Response Time: {results['total_response_time']:.6f} seconds")
    
    if results['success']:
        print("✅ Test Status: SUCCESS")
        if results['total_response_time'] > 3.0:
            print("⚠️  WARNING: Response time exceeded 3 second target!")
    else:
        print("❌ Test Status: FAILED")
    
    print("="*70 + "\n")


async def run_single_test():
    """Run a single test iteration."""
    patient_data = generate_random_patient()
    
    print(f"\n🧪 Running test with: {patient_data['user_id']}")
    print(f"   Cancer Type: {patient_data['cancer_type']}")
    print(f"   Location: {patient_data['location']}")
    
    results = await test_api_endpoint(patient_data)
    print_results(results)
    save_results_to_csv(results)
    
    return results


async def run_continuous_tests():
    """Run tests continuously every 30 minutes for 1 week."""
    end_time = datetime.now() + timedelta(days=TEST_DURATION_DAYS)
    test_count = 0
    
    print("\n" + "🚀"*35)
    print("MaleCare ChatBot - Automated API Performance Testing")
    print("🚀"*35)
    print(f"\nStart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Interval: {TEST_INTERVAL_MINUTES} minutes")
    print(f"Expected Tests: {int((TEST_DURATION_DAYS * 24 * 60) / TEST_INTERVAL_MINUTES)}")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        while datetime.now() < end_time:
            test_count += 1
            print(f"\n{'='*70}")
            print(f"Test #{test_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")
            
            await run_single_test()
            
            # Calculate next run time
            next_run = datetime.now() + timedelta(minutes=TEST_INTERVAL_MINUTES)
            
            if next_run > end_time:
                print("\n✅ Test duration complete!")
                break
            
            print(f"\n⏰ Next test at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Waiting {TEST_INTERVAL_MINUTES} minutes...")
            
            # Sleep until next test
            await asyncio.sleep(TEST_INTERVAL_MINUTES * 60)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
    
    print(f"\n{'='*70}")
    print(f"Testing Complete!")
    print(f"Total Tests Run: {test_count}")
    print(f"Results saved to: {RESULTS_DIR}")
    print(f"{'='*70}\n")


async def run_quick_test():
    """Run a quick test (single iteration) for verification."""
    print("\n🔬 Running Quick Test (Single Iteration)")
    print("="*70)
    
    await run_single_test()
    
    print("\n✅ Quick test complete!")
    print(f"Results saved to: {RESULTS_DIR}")
    print("\nTo run the full week-long test, use: python automated_api_tests.py --continuous")


if __name__ == "__main__":
    import sys
    
    if "--continuous" in sys.argv or "-c" in sys.argv:
        # Run continuous testing for 1 week
        asyncio.run(run_continuous_tests())
    else:
        # Run quick test (single iteration)
        asyncio.run(run_quick_test())
