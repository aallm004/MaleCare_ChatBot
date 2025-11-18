import httpx
from app.utils.config import settings

async def search_clinical_trials(condition: str, location: str):
    """
    Pseudo-query to ClinicalTrials.gov API v2 (placeholder).
    In production, build query parameters correctly per their docs.
    """
    base_url = settings.CLINICALTRIALS_API_BASE
    params = {
        "query.term": condition,
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
                "title": f"A Study for {condition} in {location}",
                "phase": "Phase 2",
                "status": "Recruiting",
                "location": location,
                "link": f"https://clinicaltrials.gov/study/NCT12345678"
            }
        ]