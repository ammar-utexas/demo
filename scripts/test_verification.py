"""Simulate a patient call and verification through Connect Health."""
import httpx

PMS_URL = "http://localhost:8000"


def simulate_verification():
    """
    Simulates what happens when Maria Garcia calls the practice.
    In production, Amazon Connect captures the phone number automatically
    and the Patient Verification Agent handles the conversation.
    """
    print("=" * 60)
    print("SIMULATING PATIENT CALL — VERIFICATION FLOW")
    print("=" * 60)

    # Step 1: Lambda identifies patient by phone number
    print("\n[1] Patient calls from +1-512-555-1234")
    print("    Lambda invoked by contact flow...")

    with httpx.Client(base_url=PMS_URL) as client:
        # Simulate Lambda patient lookup
        response = client.get("/patients/", params={"phone": "5125551234"})
        patients = response.json()

        if isinstance(patients, list) and patients:
            patient = patients[0]
            print(f"    Found: {patient['first_name']} {patient['last_name']}")
            print(f"    DOB: {patient['date_of_birth']}")
        elif isinstance(patients, dict) and patients.get("items"):
            patient = patients["items"][0]
            print(f"    Found: {patient['first_name']} {patient['last_name']}")
            print(f"    DOB: {patient['date_of_birth']}")
        else:
            print("    No patient found for this phone number.")
            print(f"    Response: {patients}")
            return

    # Step 2: Patient Verification Agent confirms identity
    print("\n[2] Patient Verification Agent asks: 'Can you confirm your date of birth?'")
    print("    Patient says: 'April 15th, 1958'")

    with httpx.Client(base_url=PMS_URL) as client:
        response = client.post(
            "/connect-health/verify-patient",
            json={
                "contact_id": "test-contact-001",
                "spoken_name": "Maria Garcia",
                "spoken_dob": "1958-04-15",
                "caller_phone": "+15125551234",
            },
        )
        result = response.json()

    print(f"\n[3] Verification Result:")
    print(f"    Verified: {result.get('verified', 'N/A')}")
    print(f"    Confidence: {result.get('confidence', 'N/A')}")
    print(f"    Patient ID: {result.get('patient_id', 'N/A')}")
    print(f"    Method: {result.get('verification_method', 'N/A')}")

    if result.get("verified"):
        print("\n    Patient verified! Routing to PatientAccess queue...")
    else:
        print("\n    Verification failed. Transferring to agent for manual verification.")


if __name__ == "__main__":
    simulate_verification()
