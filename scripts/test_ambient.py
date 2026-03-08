"""Simulate ambient documentation during an ophthalmology encounter."""
import httpx
import time
import os

PMS_URL = "http://localhost:8000"
PATIENT_ID = os.environ.get("TEST_PATIENT_ID", "test-patient-001")

# Simulated encounter transcript (what the ambient agent would capture)
SIMULATED_TRANSCRIPT = """
Dr. Patel: Good morning, Maria. How have your eyes been since your last injection?

Maria Garcia: Good morning, doctor. My right eye has been a little blurry this week,
especially when reading. The left eye seems fine.

Dr. Patel: Let me take a look. I'm going to do an OCT scan of both eyes today.
[Performs OCT scan]
The OCT shows some subretinal fluid in the right eye. The left eye looks stable.
Your visual acuity today is 20/40 in the right eye and 20/25 in the left.

Maria Garcia: Is that worse than last time?

Dr. Patel: The right eye was 20/30 last visit, so yes, slightly decreased.
Given the fluid and the decreased vision, I'd recommend we do another
Eylea injection in the right eye today. We'll keep the left eye on monitoring.

Maria Garcia: Okay, let's do it.

Dr. Patel: I'll numb the eye first with topical anesthesia, then prep with
betadine, and administer the 2mg Eylea injection. You'll feel some pressure
but it shouldn't be painful.
[Performs intravitreal injection]
All done. The injection went smoothly. I'd like to see you back in 4 weeks
for another OCT and we'll decide on the next injection timing then.

Maria Garcia: Thank you, doctor.
"""


def simulate_ambient_documentation():
    print("=" * 60)
    print("AMBIENT DOCUMENTATION — OPHTHALMOLOGY ENCOUNTER")
    print("=" * 60)

    with httpx.Client(base_url=PMS_URL, timeout=60) as client:
        # Step 1: Start ambient session
        print("\n[1] Starting ambient session...")
        response = client.post(
            "/connect-health/ambient/start",
            json={
                "encounter_id": "test-encounter-001",
                "patient_id": PATIENT_ID,
                "specialty": "ophthalmology",
                "note_template": "SOAP",
            },
        )
        session = response.json()
        session_id = session.get("session_id", "test-session-001")
        print(f"    Session ID: {session_id}")
        print(f"    Status: {session.get('status', 'active')}")

        # Step 2: Simulate encounter duration
        print("\n[2] Encounter in progress (simulating 5-second recording)...")
        print(f"    Transcript preview:")
        for line in SIMULATED_TRANSCRIPT.strip().split("\n")[:6]:
            print(f"    {line.strip()}")
        print("    ...")
        time.sleep(5)

        # Step 3: Stop session and get generated note
        print("\n[3] Stopping ambient session and generating note...")
        response = client.post(
            "/connect-health/ambient/stop",
            json={
                "session_id": session_id,
                "encounter_id": "test-encounter-001",
            },
        )
        result = response.json()

    # Display results
    print(f"\n{'─' * 60}")
    print("GENERATED CLINICAL NOTE (SOAP)")
    print(f"{'─' * 60}")
    print(result.get("clinical_note", "(no note generated)"))

    # Display suggested codes
    print(f"\n{'─' * 60}")
    print("SUGGESTED ICD-10 CODES")
    print(f"{'─' * 60}")
    for code in result.get("icd10_suggestions", []):
        conf = code.get("confidence", 0) * 100
        print(f"  [{conf:.0f}%] {code['code']} — {code['description']}")

    print(f"\n{'─' * 60}")
    print("SUGGESTED CPT CODES")
    print(f"{'─' * 60}")
    for code in result.get("cpt_suggestions", []):
        conf = code.get("confidence", 0) * 100
        print(f"  [{conf:.0f}%] {code['code']} — {code['description']}")

    print(f"\n{'─' * 60}")
    print("CLINICIAN ACTION REQUIRED")
    print(f"{'─' * 60}")
    print("  Review the generated note and codes above.")
    print("  Accept → saves to encounter record and queues for billing.")
    print("  Edit → modify note in PMS editor before saving.")
    print("  Discard → delete generated note; document manually.")


if __name__ == "__main__":
    simulate_ambient_documentation()
