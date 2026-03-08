"""Retrieve pre-visit summary from Connect Health Patient Insights Agent."""
import httpx
import json
import os

PMS_URL = "http://localhost:8000"
PATIENT_ID = os.environ.get("TEST_PATIENT_ID", "test-patient-001")


def get_pre_visit_summary():
    print("=" * 60)
    print("PRE-VISIT SUMMARY — PATIENT INSIGHTS AGENT")
    print("=" * 60)

    with httpx.Client(base_url=PMS_URL) as client:
        response = client.get(f"/connect-health/insights/{PATIENT_ID}")
        insights = response.json()

    print(f"\nPatient: {PATIENT_ID}")
    print(f"Generated: {insights.get('generated_at', 'N/A')}")

    if insights.get("summary"):
        print(f"\n--- Summary ---")
        print(insights["summary"])

    if insights.get("active_medications"):
        print(f"\n--- Active Medications ---")
        for med in insights["active_medications"]:
            print(f"  - {med.get('name', 'N/A')}: {med.get('dose', '')} {med.get('frequency', '')}")

    if insights.get("care_gaps"):
        print(f"\n--- Care Gaps ---")
        for gap in insights["care_gaps"]:
            print(f"  - {gap}")

    print(f"\nThis summary is displayed to Dr. Patel before she enters the exam room.")


if __name__ == "__main__":
    get_pre_visit_summary()
