"""Create a synthetic patient for Connect Health testing."""
import httpx

PMS_URL = "http://localhost:8000"

PATIENT_DATA = {
    "first_name": "Maria",
    "last_name": "Garcia",
    "date_of_birth": "1958-04-15",
    "gender": "Female",
    "phone": "5125551234",
    "email": "maria.garcia@example.com",
    "address": "1234 Main St, Austin, TX 78701",
}


def create_patient():
    with httpx.Client(base_url=PMS_URL) as client:
        response = client.post("/patients/", json=PATIENT_DATA)
        response.raise_for_status()
        patient = response.json()
        print(f"Created patient: {patient['id']}")
        print(f"Name: {patient['first_name']} {patient['last_name']}")
        print(f"DOB: {patient['date_of_birth']}")
        print(f"Phone: {patient.get('phone', 'N/A')}")
        return patient


if __name__ == "__main__":
    create_patient()
