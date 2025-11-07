import requests

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

def search_clinical_trials(disease, location=None, status="Recruiting", limit=5):
    params = {
        "query.term": disease,
        "filter.overallStatus": status,
        "pageSize": limit,
    }
    if location:
        params["filter.locations"] = location

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None

def extract_trial_info(data):
    trials = []
    for study in data.get("studies", []):
        protocol = study.get("protocolSection", {})
        id_module = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        contact_module = protocol.get("contactsLocationsModule", {})

        nct_id = id_module.get("nctId", "N/A")
        title = id_module.get("briefTitle", "No title available")
        status = status_module.get("overallStatus", "Unknown")
        contact_info = contact_module.get("centralContacts", [])

        contact_str = (
            ", ".join([c.get("name", "") for c in contact_info]) if contact_info else "N/A"
        )

        trials.append({
            "NCT ID": nct_id,
            "Title": title,
            "Status": status,
            "Contact": contact_str,
        })
    return trials


    #FAQ Model


    FAQ_RESPONSES = {
    "eligibility": "Eligibility criteria vary by trial. Typically, they include factors like cancer type, stage, age, and medical history.",
    "location": "Most trials list their locations in the ClinicalTrials.gov entry. We can search trials in your preferred state or country.",
    "contact": "Each trial has a contact person or site listed. I can show that information when you search a trial.",
    "default": "I can help you find active clinical trials, or answer basic questions about how trials work."
}

def get_faq_response(user_input):
    user_input = user_input.lower()
    for keyword, response in FAQ_RESPONSES.items():
        if keyword in user_input:
            return response
    return FAQ_RESPONSES["default"]

    

    #Chatbot Logic


    from clinicaltrials_api import search_clinical_trials, extract_trial_info
from faq_module import get_faq_response

def handle_user_input(user_input):
    if "trial" in user_input.lower():
        # Simple heuristic: extract cancer type from input
        disease = user_input.replace("find trials for", "").strip()
        data = search_clinical_trials(disease)
        if data:
            results = extract_trial_info(data)
            response = "Here are some matching trials:\n\n"
            for trial in results:
                response += (
                    f"🏷️ {trial['Title']}\n"
                    f"🔹 NCT ID: {trial['NCT ID']}\n"
                    f"📍 Status: {trial['Status']}\n"
                    f"☎️ Contact: {trial['Contact']}\n\n"
                )
            return response
        else:
            return "I encountered a problem fetching trial information."
    else:
        return get_faq_response(user_input)

def main():
    print("🤖 Cancer Clinical Trial Chatbot\nType 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        print("Bot:", handle_user_input(user_input))

if __name__ == "__main__":
    main()