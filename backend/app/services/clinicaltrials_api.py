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
        stage: Cancer stage (optional)
        age: Patient age (optional)
    
    Returns:
        List of clinical trial dictionaries with real trial data
    """
    base_url = settings.CLINICALTRIALS_API_BASE
    
    # Convert location format: "Boston Massachusetts" -> "Boston, MA"
    location_formatted = format_location_for_api(location)
    
    # Build API parameters with correct format
    params = {
        "query.cond": cancer_type,              # Search by condition/disease
        "query.locn": location_formatted,        # Location in "City, STATE" format
        "filter.overallStatus": "RECRUITING",    # Only recruiting trials
        "pageSize": 10,                          # Get up to 10 results
        "format": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(f"Calling ClinicalTrials.gov API for {cancer_type} in {location}")
            
            # Make the REAL API call with location filter
            response = await client.get(f"{base_url}/studies", params=params)
            response.raise_for_status()
            
            data = response.json()
            studies = data.get("studies", [])
            
            # Parse and format the results
            trials = parse_trials(studies, location)
            
            logger.info(f"Found {len(trials)} trials for {cancer_type} in {location}")
            
            # If no trials found locally, search nationwide
            if not trials or len(trials) == 0:
                logger.info(f"No local trials found, searching nationwide for {cancer_type}")
                
                # Remove location filter for broader search
                params_nationwide = {
                    "query.cond": cancer_type,
                    "filter.overallStatus": "RECRUITING",
                    "pageSize": 10,
                    "format": "json"
                }
                
                response_nationwide = await client.get(f"{base_url}/studies", params=params_nationwide)
                response_nationwide.raise_for_status()
                
                data_nationwide = response_nationwide.json()
                studies_nationwide = data_nationwide.get("studies", [])
                
                trials = parse_trials(studies_nationwide, location, is_nationwide=True)
                logger.info(f"Found {len(trials)} trials nationwide for {cancer_type}")
            
            return trials
            
    except httpx.TimeoutException:
        logger.error(f"Timeout calling ClinicalTrials.gov API")
        return get_error_response(cancer_type, location, "Request timed out")
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error calling ClinicalTrials.gov API: {e}")
        return get_error_response(cancer_type, location, "API unavailable")
        
    except Exception as e:
        logger.error(f"Unexpected error calling ClinicalTrials.gov API: {e}")
        return get_error_response(cancer_type, location, "Unexpected error")


def format_location_for_api(location: str) -> str:
    """
    Convert location format for the API.
    
    Examples:
        "Boston Massachusetts" -> "Boston, MA"
        "New York New York" -> "New York, NY"
        "Los Angeles California" -> "Los Angeles, CA"
    
    Args:
        location: City and state as a string
    
    Returns:
        Formatted location string "City, STATE"
    """
    state_abbreviations = {
        "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
        "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
        "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
        "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
        "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
        "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
        "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
        "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
        "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
        "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
        "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
        "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
        "wisconsin": "WI", "wyoming": "WY"
    }
    
    try:
        parts = location.strip().split()
        if len(parts) >= 2:
            # Last word is state, everything else is city
            state_full = parts[-1].lower()
            city = " ".join(parts[:-1])
            
            # Convert state name to abbreviation
            state_abbr = state_abbreviations.get(state_full, parts[-1])
            
            return f"{city}, {state_abbr}"
        
        # If parsing fails, return as-is
        return location
        
    except Exception:
        return location


def parse_trials(studies: List[Dict], requested_location: str, is_nationwide: bool = False) -> List[Dict[str, Any]]:
    """
    Parse API response into standardized trial format.
    
    Args:
        studies: List of study data from API
        requested_location: The location the user searched for
        is_nationwide: If True, indicates these are nationwide results (not local)
    
    Returns:
        List of formatted trial dictionaries
    """
    trials = []
    
    for study in studies:
        try:
            protocol = study.get("protocolSection", {})
            
            # Extract basic info
            identification = protocol.get("identificationModule", {})
            nct_id = identification.get("nctId", "Unknown")
            title = identification.get("briefTitle") or identification.get("officialTitle", "Untitled Study")
            
            # Extract status
            status_module = protocol.get("statusModule", {})
            status = status_module.get("overallStatus", "Unknown")
            
            # Extract phase
            design = protocol.get("designModule", {})
            phases = design.get("phases", [])
            phase = phases[0].replace("PHASE", "Phase ") if phases else "Not Specified"
            
            # Extract location info
            contacts_locations = protocol.get("contactsLocationsModule", {})
            locations = contacts_locations.get("locations", [])
            
            trial_location = requested_location
            facility = "Multiple Sites"
            
            if locations:
                first_loc = locations[0]
                facility = first_loc.get("facility", "Unknown Facility")
                city = first_loc.get("city", "")
                state = first_loc.get("state", "")
                if city and state:
                    trial_location = f"{city} {state}"
            
            # Extract sponsor
            sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
            lead_sponsor = sponsor_module.get("leadSponsor", {})
            sponsor = lead_sponsor.get("name", "Unknown Sponsor")
            
            # Build trial dictionary
            trial = {
                "nct_id": nct_id,
                "title": title,
                "phase": phase,
                "status": status.title(),
                "location": trial_location,
                "facility": facility,
                "sponsor": sponsor,
                "link": f"https://clinicaltrials.gov/study/{nct_id}",
                "is_nationwide": is_nationwide  # Flag to indicate if this is a nationwide search result
            }
            
            trials.append(trial)
            
        except Exception as e:
            logger.warning(f"Error parsing study: {e}")
            continue
    
    return trials


def get_error_response(cancer_type: str, location: str, error_msg: str) -> List[Dict[str, Any]]:
    """
    Return a helpful error message when API fails.
    Ensures the chatbot doesn't break completely.
    
    Args:
        cancer_type: Type of cancer searched
        location: Location searched
        error_msg: Error description
    
    Returns:
        List with a single error message
    """
    return [
        {
            "nct_id": "API_ERROR",
            "title": f"Unable to fetch trials at this time ({error_msg})",
            "phase": "N/A",
            "status": "API Unavailable",
            "location": location,
            "facility": "ClinicalTrials.gov",
            "sponsor": "System",
            "link": "https://clinicaltrials.gov",
            "message": f"We're having trouble connecting to ClinicalTrials.gov. Please try again in a moment."
        }
    ]