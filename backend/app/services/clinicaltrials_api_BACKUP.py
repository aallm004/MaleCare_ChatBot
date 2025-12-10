import httpx
from app.utils.config import settings
from typing import Optional

async def search_clinical_trials(
        cancer_type: str,
        location: str,
        stage: Optional[str] = None,
        age: Optional[int] = None
    ):
    """
    Query to ClinicalTrials.gov API v2.
    """
    base_url = settings.CLINICALTRIALS_API_BASE
    params = {
        "query.term": cancer_type,
        "filter.overallStatus": "Recruiting",
        "filter.location": location,
        "pageSize": 3
    }

    async with httpx.AsyncClient() as client:
        # This call is stubbed for now
        # response = await client.get(f"{base_url}/studies", params=params)
        # data = response.json()
        # return data["studies"]

        # Mocked results
        return [
            {
                "nct_id": "NCT12345678",
                "title": f"A Study for {cancer_type} in {location}",
                "phase": "Phase 2",
                "status": "Recruiting",
                "location": location,
                "link": f"https://clinicaltrials.gov/study/NCT12345678"
            }
        ]