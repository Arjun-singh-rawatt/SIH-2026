import asyncio
import os
import sys
from datetime import datetime, timezone
import motor.motor_asyncio
from dotenv import load_dotenv

# Add the project root to the python path so we can import app modules if needed
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "sift_dev")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DATABASE]

REPORTS = [
    {
        "report_id": "OIL-DEMO-001",
        "raw_report_text": "Maintenance crew was preparing to open a hydrocarbon process line. Isolation points were identified, but zero-energy verification had not been completed. Residual pressure was suspected while workers were positioned near the opening point.",
        "metadata": {
            "reporter_id": "USR-001",
            "reporter_name": "Alok Sharma",
            "facility_id": "FAC-DEMO-01",
            "facility_name": "Demo Process Plant A",
            "region": "Demo Operations",
            "location": "Process Plant A, Energy Isolation Area",
            "report_type": "Unsafe Condition"
        },
        "analysis": {
            "language": "English",
            "activity": "Line breaking / opening process equipment",
            "hazard": "Pressure / stored energy",
            "sif_precursor": "Yes",
            "sif_potential": "Critical",
            "precursor_category": "Energy isolation failure",
            "life_saving_rule": "Energy Isolation",
            "failed_barrier": "Verified energy isolation",
            "barrier_status": "Failed",
            "evidence_phrase": "zero-energy verification had not been completed",
            "confidence": 98.0
        },
        "risk": {
            "urgency_score": 95,
            "risk_level": "Critical",
            "escalation_required": True
        },
        "review": {
            "status": "Pending Review",
            "reviewer_id": None,
            "reviewed_at": None
        },
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-002",
        "raw_report_text": "Drilling activity continued after abnormal pressure was observed at the wellhead. Well-control barriers were not immediately confirmed available.",
        "metadata": {
            "reporter_id": "USR-002",
            "facility_id": "FAC-DEMO-02",
            "facility_name": "Demo Wellsite B",
            "location": "Wellhead Pressure Control Area",
            "report_type": "Near Miss"
        },
        "analysis": {
            "language": "English",
            "sif_precursor": "Yes",
            "sif_potential": "Critical",
            "precursor_category": "Well Control / Drilling",
            "confidence": 96.0
        },
        "risk": {"urgency_score": 92},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-003",
        "raw_report_text": "Line breaking activity was started on a process line containing possible hydrocarbon residue. Pressure status had not been confirmed before loosening the flange, and personnel were standing within the potential line-of-fire zone.",
        "metadata": {
            "facility_id": "FAC-DEMO-03",
            "facility_name": "Demo Tank Farm",
            "location": "Tank Farm Line Breaking Zone",
            "report_type": "Unsafe Act"
        },
        "analysis": {
            "language": "English",
            "sif_precursor": "Yes",
            "sif_potential": "Critical",
            "precursor_category": "Line breaking / loss of containment",
            "confidence": 95.0
        },
        "risk": {"urgency_score": 90},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-004",
        "raw_report_text": "A worker was preparing to enter a vessel for inspection. Atmospheric testing had not been completed and the standby attendant had not yet been positioned at the entry point.",
        "metadata": {
            "facility_id": "FAC-DEMO-04",
            "facility_name": "Demo Maintenance Area",
            "location": "Vessel Entry Point",
            "report_type": "Unsafe Condition"
        },
        "analysis": {
            "language": "English",
            "sif_precursor": "Yes",
            "sif_potential": "Critical",
            "precursor_category": "Confined-space control failure",
            "life_saving_rule": "Confined Space",
            "confidence": 97.0
        },
        "risk": {"urgency_score": 94},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-005",
        "raw_report_text": "Forklift was moving through a shared operating area while pedestrians were working nearby. No clearly separated pedestrian route was available at the time of observation.",
        "metadata": {
            "facility_id": "FAC-DEMO-05",
            "facility_name": "Demo Loading Bay",
            "location": "Vehicle Movement Route",
            "report_type": "Unsafe Condition"
        },
        "analysis": {
            "language": "English",
            "sif_precursor": "Yes",
            "sif_potential": "High",
            "precursor_category": "Vehicle / Mobile Equipment",
            "confidence": 90.0
        },
        "risk": {"urgency_score": 80},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-006",
        "raw_report_text": "Hot work was being prepared near equipment containing flammable material. The work area was not fully cleared of combustible material and fire-watch arrangements were not confirmed.",
        "metadata": {
            "facility_id": "FAC-DEMO-06",
            "facility_name": "Demo Fabrication Area",
            "location": "Fabrication Bay - Hot Work Zone",
            "report_type": "Unsafe Act"
        },
        "analysis": {
            "language": "English",
            "sif_precursor": "Yes",
            "sif_potential": "High",
            "precursor_category": "Hot work / ignition control",
            "life_saving_rule": "Hot Work",
            "confidence": 92.0
        },
        "risk": {"urgency_score": 82},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-007",
        "raw_report_text": "A worker was carrying out maintenance from an elevated platform. The worker was connected to fall-protection equipment, but the attachment arrangement had not been verified before work started.",
        "metadata": {
            "facility_id": "FAC-DEMO-07",
            "facility_name": "Demo Pipe Rack",
            "location": "Pipe Rack Level 3",
            "report_type": "Unsafe Condition"
        },
        "analysis": {
            "language": "English",
            "sif_precursor": "Yes",
            "sif_potential": "High",
            "precursor_category": "Work at Height",
            "life_saving_rule": "Working at Height",
            "confidence": 88.0
        },
        "risk": {"urgency_score": 78},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-008",
        "raw_report_text": "A section of walkway was partially obstructed by unused materials, reducing clear access for personnel and potentially restricting movement during an emergency.",
        "metadata": {
            "facility_id": "FAC-DEMO-08",
            "facility_name": "Demo Utility Area",
            "location": "Main Utility Walkway",
            "report_type": "Unsafe Condition"
        },
        "analysis": {
            "language": "English",
            "sif_precursor": "No",
            "sif_potential": "Low",
            "precursor_category": "Housekeeping / Access",
            "confidence": 99.0
        },
        "risk": {"urgency_score": 20},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-009",
        "raw_report_text": "Pump maintenance ke time isolation confirm nahi kiya gaya tha. Line mein pressure zero hai ya nahi properly verify nahi hua, aur worker opening point ke bilkul paas khada tha.",
        "metadata": {
            "facility_id": "FAC-DEMO-01",
            "facility_name": "Demo Process Plant A",
            "location": "Pump Maintenance Area",
            "report_type": "Unsafe Condition"
        },
        "analysis": {
            "language": "Hinglish",
            "sif_precursor": "Yes",
            "sif_potential": "Critical",
            "precursor_category": "Energy isolation failure",
            "life_saving_rule": "Energy Isolation",
            "confidence": 96.0
        },
        "risk": {"urgency_score": 93},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-010",
        "raw_report_text": "Forklift aur pedestrians same route use kar rahe the. Pedestrian ke liye separate path available nahi tha aur vehicle movement ke time exclusion zone bhi maintain nahi kiya gaya.",
        "metadata": {
            "facility_id": "FAC-DEMO-05",
            "facility_name": "Demo Loading Bay",
            "location": "Vehicle Movement Route",
            "report_type": "Unsafe Condition"
        },
        "analysis": {
            "language": "Hinglish",
            "sif_precursor": "Yes",
            "sif_potential": "High",
            "precursor_category": "Vehicle / Mobile Equipment",
            "confidence": 90.0
        },
        "risk": {"urgency_score": 81},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-011",
        "raw_report_text": "कर्मचारी ने वेसल में प्रवेश की तैयारी शुरू कर दी, लेकिन गैस टेस्ट अभी पूरा नहीं हुआ था और आपातकालीन बचाव की व्यवस्था भी सुनिश्चित नहीं की गई थी।",
        "metadata": {
            "facility_id": "FAC-DEMO-04",
            "facility_name": "Demo Maintenance Area",
            "location": "Vessel Entry Point",
            "report_type": "Unsafe Condition"
        },
        "analysis": {
            "language": "Hindi",
            "sif_precursor": "Yes",
            "sif_potential": "Critical",
            "precursor_category": "Confined-space control failure",
            "life_saving_rule": "Confined Space",
            "confidence": 94.0
        },
        "risk": {"urgency_score": 92},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    },
    {
        "report_id": "OIL-DEMO-012",
        "raw_report_text": "Platform par kaam karte waqt worker ka lanyard connected tha, lekin anchorage point approved hai ya nahi verify nahi kiya gaya.",
        "metadata": {
            "facility_id": "FAC-DEMO-07",
            "facility_name": "Demo Pipe Rack",
            "location": "Pipe Rack Level 3",
            "report_type": "Unsafe Condition"
        },
        "analysis": {
            "language": "Hinglish",
            "sif_precursor": "Yes",
            "sif_potential": "Moderate",
            "precursor_category": "Work at Height",
            "life_saving_rule": "Working at Height",
            "confidence": 85.0
        },
        "risk": {"urgency_score": 60},
        "review": {"status": "Pending Review"},
        "data_status": "Synthetic demo",
    }
]


async def seed():
    print(f"Connected to db: {MONGODB_DATABASE}")
    reports_col = db.reports

    # Clean existing demo data if reset is passed
    if "--reset" in sys.argv:
        print("Reset flag detected. Removing all synthetic reports...")
        await reports_col.delete_many({"data_status": "Synthetic demo"})

    now = datetime.now(timezone.utc).isoformat()
    inserted = 0

    for rep in REPORTS:
        rep["created_at"] = now
        rep["updated_at"] = now
        
        # Upsert
        result = await reports_col.update_one(
            {"report_id": rep["report_id"]},
            {"$set": rep},
            upsert=True
        )
        if result.upserted_id or result.modified_count:
            inserted += 1

    print(f"Upserted {inserted} synthetic reports.")

    # Create Indexes
    await reports_col.create_index("report_id", unique=True)
    await reports_col.create_index("created_at")
    await reports_col.create_index("metadata.facility_id")
    await reports_col.create_index("analysis.sif_potential")
    await reports_col.create_index("review.status")
    await reports_col.create_index("risk.urgency_score")
    
    print("MongoDB indexes created successfully.")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
