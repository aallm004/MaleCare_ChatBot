"""
Weekend API Monitoring - Simulates Real Patient Conversations
Runs every 30 minutes, logs results to CSV for Monday review

This script:
- Simulates realistic patient conversations
- Calls the real ClinicalTrials.gov API via /intake endpoint
- Logs query times, errors, and full conversation flow
- Runs continuously from Friday evening through Monday morning
"""

import asyncio
import httpx
import csv
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "http://localhost:8000"
CSV_FILE = Path(__file__).parent / "weekend_api_monitoring.csv"

# Realistic patient scenarios
PATIENT_SCENARIOS = [
    {
        "name": "John Smith",
        "user_id": "patient_001",
        "cancer_type": "prostate cancer",
        "stage": "2",
        "age": 67,
        "sex": "male",
        "location": "Boston Massachusetts",
        "comorbidities": [],
        "prior_treatments": []
    },
    {
        "name": "Mary Johnson",
        "user_id": "patient_002",
        "cancer_type": "breast cancer",
        "stage": "3",
        "age": 52,
        "sex": "female",
        "location": "Los Angeles California",
        "comorbidities": ["diabetes"],
        "prior_treatments": ["chemotherapy"]
    },
    {
        "name": "Robert Chen",
        "user_id": "patient_003",
        "cancer_type": "lung cancer",
        "stage": "4",
        "age": 61,
        "sex": "male",
        "location": "New York New York",
        "comorbidities": [],
        "prior_treatments": []
    },
    {
        "name": "Sarah Williams",
        "user_id": "patient_004",
        "cancer_type": "breast cancer",
        "stage": "1",
        "age": 45,
        "sex": "female",
        "location": "Chicago Illinois",
        "comorbidities": [],
        "prior_treatments": []
    },
    {
        "name": "Michael Davis",
        "user_id": "patient_005",
        "cancer_type": "colorectal cancer",
        "stage": "3",
        "age": 58,
        "sex": "male",
        "location": "Houston Texas",
        "comorbidities": ["hypertension"],
        "prior_treatments": ["surgery"]
    },
    {
        "name": "Linda Martinez",
        "user_id": "patient_006",
        "cancer_type": "ovarian cancer",
        "stage": "2",
        "age": 63,
        "sex": "female",
        "location": "Phoenix Arizona",
        "comorbidities": [],
        "prior_treatments": []
    },
    {
        "name": "James Wilson",
        "user_id": "patient_007",
        "cancer_type": "lung cancer",
        "stage": "3",
        "age": 69,
        "sex": "male",
        "location": "Philadelphia Pennsylvania",
        "comorbidities": ["COPD"],
        "prior_treatments": ["radiation"]
    },
    {
        "name": "Patricia Brown",
        "user_id": "patient_008",
        "cancer_type": "breast cancer",
        "stage": "2",
        "age": 48,
        "sex": "female",
        "location": "San Antonio Texas",
        "comorbidities": [],
        "prior_treatments": []
    },
    {
        "name": "David Miller",
        "user_id": "patient_009",
        "cancer_type": "melanoma",
        "stage": "2",
        "age": 55,
        "sex": "male",
        "location": "San Diego California",
        "comorbidities": [],
        "prior_treatments": ["immunotherapy"]
    },
    {
        "name": "Jennifer Garcia",
        "user_id": "patient_010",
        "cancer_type": "pancreatic cancer",
        "stage": "3",
        "age": 64,
        "sex": "female",
        "location": "Dallas Texas",
        "comorbidities": ["diabetes"],
        "prior_treatments": []
    },
    # Small town scenarios to test nationwide fallback
    {
        "name": "Tom Henderson",
        "user_id": "patient_011",
        "cancer_type": "lung cancer",
        "stage": "2",
        "age": 59,
        "sex": "male",
        "location": "Siloam Springs Arkansas",
        "comorbidities": [],
        "prior_treatments": []
    },
    {
        "name": "Emily Cooper",
        "user_id": "patient_012",
        "cancer_type": "breast cancer",
        "stage": "1",
        "age": 43,
        "sex": "female",
        "location": "Bend Oregon",
        "comorbidities": [],
        "prior_treatments": []
    }
]


def initialize_csv():
    """Create CSV file with headers if it doesn't exist"""
    if not CSV_FILE.exists():
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp',
                'Patient_Name',
                'User_ID',
                'Cancer_Type',
                'Stage',
                'Age',
                'Sex',
                'Location',
                'Comorbidities',
                'Prior_Treatments',
                'API_Query_Time_Seconds',
                'HTTP_Status_Code',
                'Trials_Found',
                'Has_Nationwide_Results',
                'Error_Message',
                'Response_Message',
                'Sample_Trial_NCT_ID',
                'Sample_Trial_Title',
                'Sample_Trial_Location',
                'Sample_Trial_Facility'
            ])
        logger.info(f"Created CSV file: {CSV_FILE}")
    else:
        logger.info(f"Using existing CSV file: {CSV_FILE}")


async def simulate_patient_conversation(patient: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate a real patient conversation with the chatbot
    Returns conversation data and metrics
    """
    conversation_data = {
        'timestamp': datetime.now().isoformat(),
        'patient_name': patient['name'],
        'user_id': patient['user_id'],
        'cancer_type': patient['cancer_type'],
        'stage': patient['stage'],
        'age': patient['age'],
        'sex': patient['sex'],
        'location': patient['location'],
        'comorbidities': ', '.join(patient.get('comorbidities', [])) or 'None',
        'prior_treatments': ', '.join(patient.get('prior_treatments', [])) or 'None',
        'api_query_time': 0.0,
        'http_status': 0,
        'trials_found': 0,
        'has_nationwide': False,
        'error_message': '',
        'response_message': '',
        'sample_nct_id': '',
        'sample_title': '',
        'sample_location': '',
        'sample_facility': ''
    }

    logger.info(f"\n{'='*70}")
    logger.info(f"Starting conversation for: {patient['name']}")
    logger.info(f"Cancer: {patient['cancer_type']}, Location: {patient['location']}")
    logger.info(f"{'='*70}")

    try:
        # Call /intake endpoint (which now calls the real API)
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/intake",
                json=patient
            )
            
            query_time = time.time() - start_time
            conversation_data['api_query_time'] = round(query_time, 3)
            conversation_data['http_status'] = response.status_code
            
            logger.info(f"API Response Time: {query_time:.3f} seconds")
            logger.info(f"HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract response data
                conversation_data['response_message'] = result.get('response', '')
                trials = result.get('trials', [])
                conversation_data['trials_found'] = len(trials)
                
                logger.info(f"Trials Found: {len(trials)}")
                logger.info(f"Response: {result.get('response', '')}")
                
                if trials:
                    # Check for nationwide results
                    conversation_data['has_nationwide'] = any(
                        t.get('is_nationwide', False) for t in trials
                    )
                    
                    # Store first trial as sample
                    first_trial = trials[0]
                    conversation_data['sample_nct_id'] = first_trial.get('nct_id', '')
                    conversation_data['sample_title'] = first_trial.get('title', '')[:100]
                    conversation_data['sample_location'] = first_trial.get('location', '')
                    conversation_data['sample_facility'] = first_trial.get('facility', '')
                    
                    logger.info(f"Sample Trial: {first_trial.get('nct_id')} - {first_trial.get('title', '')[:50]}...")
                    
                    if conversation_data['has_nationwide']:
                        logger.info("⚠️  Nationwide fallback triggered (small town)")
                else:
                    logger.warning("No trials returned")
                    
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                conversation_data['error_message'] = error_msg
                logger.error(f"API Error: {error_msg}")
                
    except httpx.TimeoutException as e:
        error_msg = f"Timeout after 30 seconds: {str(e)}"
        conversation_data['error_message'] = error_msg
        logger.error(f"Timeout Error: {error_msg}")
        
    except httpx.RequestError as e:
        error_msg = f"Request Error: {str(e)}"
        conversation_data['error_message'] = error_msg
        logger.error(f"Request Error: {error_msg}")
        
    except Exception as e:
        error_msg = f"Unexpected Error: {str(e)}"
        conversation_data['error_message'] = error_msg
        logger.error(f"Unexpected Error: {error_msg}")

    return conversation_data


def write_to_csv(conversation_data: Dict[str, Any]):
    """Append conversation data to CSV file"""
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            conversation_data['timestamp'],
            conversation_data['patient_name'],
            conversation_data['user_id'],
            conversation_data['cancer_type'],
            conversation_data['stage'],
            conversation_data['age'],
            conversation_data['sex'],
            conversation_data['location'],
            conversation_data['comorbidities'],
            conversation_data['prior_treatments'],
            conversation_data['api_query_time'],
            conversation_data['http_status'],
            conversation_data['trials_found'],
            conversation_data['has_nationwide'],
            conversation_data['error_message'],
            conversation_data['response_message'],
            conversation_data['sample_nct_id'],
            conversation_data['sample_title'],
            conversation_data['sample_location'],
            conversation_data['sample_facility']
        ])
    logger.info(f"✓ Logged to CSV: {CSV_FILE.name}")


async def run_test_cycle():
    """Run one complete test cycle with all patient scenarios"""
    logger.info(f"\n{'#'*70}")
    logger.info(f"Starting Test Cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'#'*70}\n")
    
    # Rotate through patient scenarios
    import random
    patient = random.choice(PATIENT_SCENARIOS)
    
    # Simulate conversation
    conversation_data = await simulate_patient_conversation(patient)
    
    # Write to CSV
    write_to_csv(conversation_data)
    
    logger.info(f"\n{'#'*70}")
    logger.info(f"Test Cycle Complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Next test in 30 minutes")
    logger.info(f"{'#'*70}\n")


async def main():
    """Main monitoring loop - runs every 30 minutes"""
    print(f"""
{'='*70}
Weekend API Monitoring Started
{'='*70}
Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test Interval: 30 minutes
CSV Log File: {CSV_FILE}
Patient Scenarios: {len(PATIENT_SCENARIOS)}
{'='*70}

Monitoring will run continuously until stopped (Ctrl+C)
    """)
    
    # Initialize CSV
    initialize_csv()
    
    test_count = 0
    
    try:
        while True:
            test_count += 1
            logger.info(f"Test #{test_count}")
            
            # Run test cycle
            await run_test_cycle()
            
            # Wait 30 minutes (1800 seconds)
            logger.info("Sleeping for 30 minutes...")
            await asyncio.sleep(1800)  # 30 minutes
            
    except KeyboardInterrupt:
        print(f"\n{'='*70}")
        print("Monitoring Stopped by User")
        print(f"Total Tests Run: {test_count}")
        print(f"CSV Log: {CSV_FILE}")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
