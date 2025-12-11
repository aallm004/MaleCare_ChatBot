"""
Real ClinicalTrials.gov API Integration
This file contains the production-ready implementation that replaces mock data
with actual API calls to ClinicalTrials.gov

To use this:
1. Backup the current clinicaltrials_api.py
2. Replace it with this file
3. Test with: python test_real_api.py
"""

import httpx
from app.utils.config import settings
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


async def search_clinical_trials(
    cancer_type: str,
    location: str,
    stage: Optional[str] = None,
    age: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Query the REAL ClinicalTrials.gov API v2 for recruiting trials.
    
    Args:
        cancer_type: Type of cancer (e.g., "breast cancer", "prostate cancer")
        location: City and state (e.g., "Boston Massachusetts")
        stage: Cancer stage (optional, e.g., "stage 2")
        age: Patient age (optional)
    
    Returns:
        List of clinical trial dictionaries with standardized fields
    """
    base_url = settings.CLINICALTRIALS_API_BASE
    
    # Build search query
    query_terms = [cancer_type]
    if stage:
        query_terms.append(stage)
    
    # Parse location (e.g., "Boston Massachusetts" -> "Massachusetts:Boston")
    location_filter = parse_location_for_api(location)
    
    # API parameters
    params = {
        "query.cond": cancer_type,  # Search by condition
        "filter.overallStatus": "RECRUITING",  # Only recruiting trials
        "pageSize": 10,  # Number of results
        "format": "json"
    }
    
    # Add location filter if successfully parsed
    if location_filter:
        params["filter.geo"] = location_filter
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(f"Calling ClinicalTrials.gov API: {base_url}/studies")
            logger.info(f"Parameters: {params}")
            
            response = await client.get(f"{base_url}/studies", params=params)
            response.raise_for_status()  # Raise error for bad status codes
            
            data = response.json()
            
            # Parse and format the results
            trials = parse_api_response(data, location)
            
            logger.info(f"Found {len(trials)} trials for {cancer_type} in {location}")
            return trials
            
    except httpx.TimeoutException:
        logger.error(f"Timeout calling ClinicalTrials.gov API")
        return get_fallback_response(cancer_type, location)
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error calling ClinicalTrials.gov API: {e}")
        return get_fallback_response(cancer_type, location)
        
    except Exception as e:
        logger.error(f"Unexpected error calling ClinicalTrials.gov API: {e}")
        return get_fallback_response(cancer_type, location)


def parse_location_for_api(location: str) -> Optional[str]:
    """
    Convert location string to API filter format.
    
    Examples:
        "Boston Massachusetts" -> "United States:Massachusetts:Boston"
        "New York New York" -> "United States:New York:New York"
        "Phoenix Arizona" -> "United States:Arizona:Phoenix"
    
    Args:
        location: City and state string
    
    Returns:
        Formatted location string for API, or None if parsing fails
    """
    try:
        parts = location.strip().split()
        if len(parts) >= 2:
            # Last part is state, everything else is city
            state = parts[-1]
            city = " ".join(parts[:-1])
            return f"United States:{state}:{city}"
        return None
    except Exception as e:
        logger.warning(f"Could not parse location '{location}': {e}")
        return None


def parse_api_response(data: Dict[str, Any], requested_location: str) -> List[Dict[str, Any]]:
    """
    Parse the ClinicalTrials.gov API response into our standardized format.
    
    Args:
        data: Raw API response JSON
        requested_location: The location the user searched for
    
    Returns:
        List of formatted trial dictionaries
    """
    trials = []
    
    # Check if we got any studies
    studies = data.get("studies", [])
    
    for study in studies:
        try:
            protocol = study.get("protocolSection", {})
            
            # Extract identification info
            identification = protocol.get("identificationModule", {})
            nct_id = identification.get("nctId", "Unknown")
            title = identification.get("briefTitle") or identification.get("officialTitle", "Untitled Study")
            
            # Extract status info
            status_module = protocol.get("statusModule", {})
            status = status_module.get("overallStatus", "Unknown")
            
            # Extract phase info
            design = protocol.get("designModule", {})
            phases = design.get("phases", [])
            phase = phases[0] if phases else "Not Specified"
            
            # Extract location info (first location if multiple)
            contacts_locations = protocol.get("contactsLocationsModule", {})
            locations = contacts_locations.get("locations", [])
            
            # Get primary location or use requested location
            trial_location = requested_location
            facility = "Multiple Sites"
            contact_info = None
            
            if locations:
                first_location = locations[0]
                facility = first_location.get("facility", "Unknown Facility")
                city = first_location.get("city", "")
                state = first_location.get("state", "")
                if city and state:
                    trial_location = f"{city} {state}"
                
                # Extract contact information
                if "contacts" in first_location and first_location["contacts"]:
                    contact = first_location["contacts"][0]
                    contact_info = {
                        "name": contact.get("name"),
                        "phone": contact.get("phone"),
                        "email": contact.get("email")
                    }
            
            # Extract sponsor
            sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
            lead_sponsor = sponsor_module.get("leadSponsor", {})
            sponsor = lead_sponsor.get("name", "Unknown Sponsor")
            
            # Build trial dictionary
            trial = {
                "nct_id": nct_id,
                "title": title,
                "phase": phase.replace("PHASE", "Phase "),  # Format: "PHASE2" -> "Phase 2"
                "status": status.title(),  # Format: "RECRUITING" -> "Recruiting"
                "location": trial_location,
                "facility": facility,
                "sponsor": sponsor,
                "link": f"https://clinicaltrials.gov/study/{nct_id}"
            }
            
            # Add contact info if available
            if contact_info:
                trial["contact"] = contact_info
            
            trials.append(trial)
            
        except Exception as e:
            logger.warning(f"Error parsing study: {e}")
            continue
    
    return trials


def get_fallback_response(cancer_type: str, location: str) -> List[Dict[str, Any]]:
    """
    Return a helpful message when the API fails.
    This ensures the chatbot doesn't break completely if the API is down.
    
    Args:
        cancer_type: Type of cancer searched
        location: Location searched
    
    Returns:
        List with a single helpful message
    """
    return [
        {
            "nct_id": "API_ERROR",
            "title": f"Unable to fetch trials for {cancer_type} at this time",
            "phase": "N/A",
            "status": "API Unavailable",
            "location": location,
            "facility": "ClinicalTrials.gov",
            "sponsor": "System",
            "link": "https://clinicaltrials.gov",
            "message": "We're having trouble connecting to ClinicalTrials.gov. Please try again in a moment, or visit ClinicalTrials.gov directly."
        }
    ]


# Helper function for testing
async def test_api_call():
    """Test function to verify API integration works"""
    print("Testing ClinicalTrials.gov API Integration...")
    print("=" * 70)
    
    test_cases = [
        ("breast cancer", "Boston Massachusetts"),
        ("prostate cancer", "New York New York"),
        ("lung cancer", "Los Angeles California"),
    ]
    
    for cancer_type, location in test_cases:
        print(f"\nSearching for: {cancer_type} in {location}")
        print("-" * 70)
        
        trials = await search_clinical_trials(cancer_type, location)
        
        print(f"Found {len(trials)} trials:")
        for i, trial in enumerate(trials[:3], 1):  # Show first 3
            print(f"\n{i}. {trial['title']}")
            print(f"   NCT ID: {trial['nct_id']}")
            print(f"   Phase: {trial['phase']}")
            print(f"   Status: {trial['status']}")
            print(f"   Facility: {trial['facility']}")
            print(f"   Link: {trial['link']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_api_call())
