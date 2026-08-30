"""Deterministic Database Seeder for SIFT Backend.

Populates authentic Oil India Limited (OIL) operational data:
- 11 HSE Users & Investigators
- 10 Operational Facilities (Upper Assam Basin, Assam Shelf, KG Basin, Rajasthan)
- 52 Detailed Field Safety Reports (UA, UC, Near Miss, Incident)
- Associated Barrier Assessments
- 32 CAPA Action Items
- Vector Index References
"""

import sys
import os
import asyncio
from datetime import datetime, timezone, timedelta

# Ensure api directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.db.models.user import User
from app.db.models.facility import Facility
from app.db.models.safety_report import SafetyReport
from app.db.models.barrier_assessment import BarrierAssessment
from app.db.models.action_item import ActionItem
from app.db.models.vector_reference import ReportVectorReference
from app.vector import get_vector_store, get_embedding_provider
from app.schemas.vector import VectorRecord
from app.utils.enums import SIFPotential, SIFPrecursor, ReviewStatus, BarrierStatus, ActionStatus, ActionPriority


SEED_USERS = [
    {
        "user_id": "USR-001",
        "name": "Alok Sharma",
        "email": "alok.sharma@oilindia.in",
        "role": "HSE Manager",
        "title": "Chief General Manager (HSE & Process Safety)",
        "facility_id": "FAC-DUL-01",
        "contact_number": "+91 94350 12841",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-002",
        "name": "Priyanka Barua",
        "email": "priyanka.barua@oilindia.in",
        "role": "Safety Officer",
        "title": "Senior Safety Engineer (Field Operations)",
        "facility_id": "FAC-DIG-02",
        "contact_number": "+91 94351 98230",
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-003",
        "name": "Devajit Neog",
        "email": "devajit.neog@oilindia.in",
        "role": "Lead Investigator",
        "title": "Superintending Safety Officer (Incident Investigation)",
        "facility_id": "FAC-MOR-03",
        "contact_number": "+91 94352 44781",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-004",
        "name": "Rituraj Gogoi",
        "email": "rituraj.gogoi@oilindia.in",
        "role": "Drilling Supervisor",
        "title": "Rig In-Charge & Drilling Superintendent",
        "facility_id": "FAC-NHK-06",
        "contact_number": "+91 94355 67120",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-005",
        "name": "Ananya Phukan",
        "email": "ananya.phukan@oilindia.in",
        "role": "Process Safety Specialist",
        "title": "Manager (Asset Integrity & Process Safety)",
        "facility_id": "FAC-MAK-04",
        "contact_number": "+91 94353 88194",
        "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-006",
        "name": "Bhaben Saikia",
        "email": "bhaben.saikia@oilindia.in",
        "role": "Pipeline Engineer",
        "title": "Senior Engineer (Crude Oil Pipeline Trunk Line)",
        "facility_id": "FAC-JOR-05",
        "contact_number": "+91 94354 22091",
        "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-007",
        "name": "Manish Rawat",
        "email": "manish.rawat@oilindia.in",
        "role": "HSE Manager",
        "title": "Deputy General Manager (Rajasthan Basin HSE)",
        "facility_id": "FAC-RAJ-09",
        "contact_number": "+91 98290 41103",
        "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-008",
        "name": "Sunita Hazarika",
        "email": "sunita.hazarika@oilindia.in",
        "role": "Safety Officer",
        "title": "HSE Field Officer (Well Servicing)",
        "facility_id": "FAC-KUM-07",
        "contact_number": "+91 94356 31920",
        "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-009",
        "name": "Karthik Raman",
        "email": "karthik.raman@oilindia.in",
        "role": "Lead Investigator",
        "title": "Senior Safety Specialist (Offshore Logistics & Marine)",
        "facility_id": "FAC-KGB-08",
        "contact_number": "+91 98491 55210",
        "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-010",
        "name": "Pranjal Borah",
        "email": "pranjal.borah@oilindia.in",
        "role": "Safety Officer",
        "title": "Safety Inspector (Gas Compression Systems)",
        "facility_id": "FAC-BAR-10",
        "contact_number": "+91 94357 11984",
        "avatar": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=120&auto=format&fit=crop&q=80",
    },
    {
        "user_id": "USR-011",
        "name": "Admin System",
        "email": "admin.sift@oilindia.in",
        "role": "Administrator",
        "title": "SIFT Platform Administrator",
        "facility_id": "FAC-DUL-01",
        "contact_number": "+91 94350 00001",
        "avatar": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=120&auto=format&fit=crop&q=80",
    },
]

SEED_FACILITIES = [
    {
        "facility_id": "FAC-DUL-01",
        "name": "Duliajan Central Hub",
        "short_name": "Duliajan Hub",
        "region": "Upper Assam Basin",
        "type": "Central Operational & Processing Hub",
        "location_description": "Central Workshop, Crude Oil Dispatch Terminal & Field HQ",
        "latitude": 27.3582,
        "longitude": 95.3184,
        "active_personnel": 1420,
        "manager": "Alok Sharma",
    },
    {
        "facility_id": "FAC-DIG-02",
        "name": "Digboi Field & Production Complex",
        "short_name": "Digboi Complex",
        "region": "Upper Assam Basin",
        "type": "Field Production & Historical Processing Plant",
        "location_description": "Compressor Area, Wellhead Clusters & Gathering Stations",
        "latitude": 27.3886,
        "longitude": 95.6322,
        "active_personnel": 890,
        "manager": "Priyanka Barua",
    },
    {
        "facility_id": "FAC-MOR-03",
        "name": "Moran Oil Field",
        "short_name": "Moran Field",
        "region": "Assam Shelf",
        "type": "Crude Oil & Associated Gas Gathering Station (GGS)",
        "location_description": "GGS-4, Separator Bank & Water Injection Station",
        "latitude": 27.1856,
        "longitude": 94.9272,
        "active_personnel": 650,
        "manager": "Devajit Neog",
    },
    {
        "facility_id": "FAC-MAK-04",
        "name": "Makum Gas Gathering Station",
        "short_name": "Makum DCS/GGS",
        "region": "Upper Assam Basin",
        "type": "High-Pressure Gas Dehydration & Compression Station",
        "location_description": "Compressor Train-3, Flare Knockout Drum Area",
        "latitude": 27.4912,
        "longitude": 95.4418,
        "active_personnel": 480,
        "manager": "Ananya Phukan",
    },
    {
        "facility_id": "FAC-JOR-05",
        "name": "Jorhat Pipeline Operations Base",
        "short_name": "Jorhat Base",
        "region": "Central Assam",
        "type": "Crude Oil Pipeline Pumping Station & Tank Farm",
        "location_description": "Mainline Pump House #2, Pig Launcher/Receiver Area",
        "latitude": 26.7509,
        "longitude": 94.2037,
        "active_personnel": 340,
        "manager": "Bhaben Saikia",
    },
    {
        "facility_id": "FAC-NHK-06",
        "name": "Naharkatiya Deep Drilling Hub",
        "short_name": "Naharkatiya Rig Hub",
        "region": "Upper Assam Basin",
        "type": "High-Pressure Exploratory Drilling & Workover Base",
        "location_description": "Rig NHK-42 Substructure, Mud Tank System & BOP Stack Area",
        "latitude": 27.2831,
        "longitude": 95.3475,
        "active_personnel": 920,
        "manager": "Rituraj Gogoi",
    },
    {
        "facility_id": "FAC-KUM-07",
        "name": "Kumchai Oil Field",
        "short_name": "Kumchai Field",
        "region": "Arunachal Foothills",
        "type": "Hilly Terrain Exploration & Production Station",
        "location_description": "Wellsite KC-14, Crude Storage Tank Farm Dome",
        "latitude": 27.5611,
        "longitude": 96.0125,
        "active_personnel": 260,
        "manager": "Sunita Hazarika",
    },
    {
        "facility_id": "FAC-KGB-08",
        "name": "KG Basin Offshore Operations Base",
        "short_name": "KG Basin Base",
        "region": "Krishna Godavari Offshore",
        "type": "Offshore Logistics, Supply Base & Subsea Well Servicing",
        "location_description": "Kakinada Jetty Supply Terminal, Crane Loading Quayside",
        "latitude": 16.9891,
        "longitude": 82.2475,
        "active_personnel": 510,
        "manager": "Karthik Raman",
    },
    {
        "facility_id": "FAC-RAJ-09",
        "name": "Rajasthan Heavy Oil Exploration Project",
        "short_name": "Rajasthan Baghewala",
        "region": "Bikaner-Nagaur Basin",
        "type": "Thermal EOR & Cyclic Steam Injection Hub",
        "location_description": "Baghewala Steam Generation Manifold & Test Separators",
        "latitude": 27.9122,
        "longitude": 72.8451,
        "active_personnel": 380,
        "manager": "Manish Rawat",
    },
    {
        "facility_id": "FAC-BAR-10",
        "name": "Barekuri Gas Gathering Station",
        "short_name": "Barekuri GGS",
        "region": "Tinsukia District",
        "type": "Associated Gas Gathering & Condensate Recovery",
        "location_description": "Condensate Stabilization Skid & Amine Sweetening Unit",
        "latitude": 27.6014,
        "longitude": 95.4219,
        "active_personnel": 290,
        "manager": "Pranjal Borah",
    },
]

# 52 Seed reports covering all critical SIF precursor categories and facilities
SEED_REPORTS = [
    {
        "report_id": "SIF-2026-00124",
        "reporter_id": "USR-002",
        "facility_id": "FAC-DIG-02",
        "location": "Compressor Area, Train-2 Header",
        "raw_report_text": "During maintenance activity on the compressor manifold, the technician started loosening bolts and removing the discharge valve without proper isolation. The line was still pressurized with 35 bar natural gas. Another technician noticed the pressure gauge needle vibrating and immediately shouted to stop the work before the flange seal blew out.",
        "language": "English",
        "report_type": "Near Miss",
        "activity": "Maintenance",
        "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
        "precursor_category": "Energy Isolation",
        "sif_precursor": "YES",
        "sif_potential": "HIGH",
        "confidence": 94.0,
        "urgency_score": 92,
        "evidence_phrase": "without proper isolation; line was still pressurized with 35 bar natural gas; removing the discharge valve",
        "life_saving_rule": "Energy Isolation",
        "failed_barrier": "Energy Isolation Verification",
        "barrier_status": "FAILED",
        "potential_consequence": "Catastrophic release of 35 bar pressurized gas resulting in high-velocity shrapnel impact and potential fatal blast/fire.",
        "ai_explanation": "The activity involved opening a pressurized containment barrier without verifying LOTO or depressurizing the 35 bar natural gas line. Had the flange seal failed under pressure, fatal blunt trauma or vapor cloud ignition would have been imminent.",
        "review_status": "PENDING",
        "created_offset_days": 2,
    },
    {
        "report_id": "SIF-2026-00125",
        "reporter_id": "USR-004",
        "facility_id": "FAC-NHK-06",
        "location": "Rig Floor NHK-42, Derrick Substructure",
        "raw_report_text": "While tripping 5-inch drill pipes, the auxiliary air hoist wire rope snapped near the thimble clamp under a 3.2-ton shock load. The suspended drill collar swung erratically through the rotary table area, narrowly missing two roughnecks standing directly in the line of fire before crashing into the drawworks console.",
        "language": "English",
        "report_type": "Near Miss",
        "activity": "Drilling Operations",
        "primary_hazard": "Dropped Heavy Object / Line of Fire",
        "precursor_category": "Lifting Operations",
        "sif_precursor": "YES",
        "sif_potential": "CRITICAL",
        "confidence": 96.0,
        "urgency_score": 97,
        "evidence_phrase": "wire rope snapped near the thimble clamp; under a 3.2-ton shock load; narrowly missing two roughnecks standing directly in the line of fire",
        "life_saving_rule": "Safe Mechanical Lifting",
        "failed_barrier": "Rigging Equipment Integrity & Exclusion Zone Enforcement",
        "barrier_status": "FAILED",
        "potential_consequence": "Direct fatal impact from a 3.2-ton uncontrolled suspended load swinging across active rig floor.",
        "ai_explanation": "Catastrophic lifting gear failure during heavy tubular hoisting. Personnel were positioned inside the swing radius line of fire, violating exclusion zone safeguards.",
        "review_status": "APPROVED",
        "created_offset_days": 3,
    },
    {
        "report_id": "SIF-2026-00126",
        "reporter_id": "USR-003",
        "facility_id": "FAC-MOR-03",
        "location": "GGS-4, 3-Phase Separator Vessel V-102",
        "raw_report_text": "Two contractor vessel cleaners opened the manway of separator V-102 and entered the confined space to scrape oily sludge without conducting pre-entry atmospheric gas testing and without continuous forced ventilation running. Standby observer was absent from the hatch. Multi-gas detector at the rim later registered 42 ppm H2S and 16.4% oxygen.",
        "language": "English",
        "report_type": "Unsafe Act",
        "activity": "Vessel Cleaning & Desanding",
        "primary_hazard": "Toxic Gas / Asphyxiation (H2S & O2 Deficiency)",
        "precursor_category": "Confined Space",
        "sif_precursor": "YES",
        "sif_potential": "CRITICAL",
        "confidence": 98.0,
        "urgency_score": 99,
        "evidence_phrase": "entered the confined space to scrape oily sludge without conducting pre-entry atmospheric gas testing; Standby observer was absent; registered 42 ppm H2S and 16.4% oxygen",
        "life_saving_rule": "Confined Space Entry",
        "failed_barrier": "Atmospheric Gas Testing & Standby Attendant Safeguard",
        "barrier_status": "FAILED",
        "potential_consequence": "Acute toxic H2S knockdown leading to rapid pulmonary edema, loss of consciousness, and fatal asphyxiation.",
        "ai_explanation": "Unauthorized entry into an untested hydrocarbon vessel containing lethal H2S levels (42 ppm exceeds IDLH 100 ppm/PEL 10 ppm) with depleted oxygen and zero standby rescue capability.",
        "review_status": "APPROVED",
        "created_offset_days": 3,
    },
    {
        "report_id": "SIF-2026-00127",
        "reporter_id": "USR-005",
        "facility_id": "FAC-MAK-04",
        "location": "Compressor Skid Area, Train-1 Knockout Line",
        "raw_report_text": "Contractor pipefitter ignited an oxy-acetylene torch to weld a structural support bracket directly onto a live flare header line while a nearby sample bleed valve was leaking hydrocarbon condensate. Flammable vapor detector 4 meters away alarmed at 38% LEL. No hot work habitat or spark containment was erected.",
        "language": "English",
        "report_type": "Unsafe Act",
        "activity": "Hot Work & Structural Welding",
        "primary_hazard": "Ignition of Hydrocarbon Vapor Cloud",
        "precursor_category": "Hot Work",
        "sif_precursor": "YES",
        "sif_potential": "HIGH",
        "confidence": 95.0,
        "urgency_score": 93,
        "evidence_phrase": "ignited an oxy-acetylene torch to weld directly onto a live flare header line; leaking hydrocarbon condensate; alarmed at 38% LEL; No hot work habitat",
        "life_saving_rule": "Hot Work & Ignition Control",
        "failed_barrier": "Combustible Gas Monitoring & Spark Containment Habitat",
        "barrier_status": "FAILED",
        "potential_consequence": "Vapor cloud ignition resulting in unconfined flash fire, flare line rupture, and fatal thermal radiation.",
        "ai_explanation": "Direct introduction of high-temperature ignition source into a classified hazardous zone with active hydrocarbon leaks and elevated LEL readings without safety enclosures.",
        "review_status": "PENDING",
        "created_offset_days": 4,
    },
    {
        "report_id": "SIF-2026-00128",
        "reporter_id": "USR-008",
        "facility_id": "FAC-KUM-07",
        "location": "Crude Storage Tank T-301 Roof",
        "raw_report_text": "Contractor painter was observed scraping rust on the curved roof edge of Crude Tank T-301 at 11 meters height in gusty winds. The worker was wearing a safety harness, but the lanyard was unhooked and dangling freely because no static lifeline had been rigged across the tank dome.",
        "language": "English",
        "report_type": "Unsafe Act",
        "activity": "Working at Height",
        "primary_hazard": "Unprotected Fall from Elevated Height (11m)",
        "precursor_category": "Working at Height",
        "sif_precursor": "YES",
        "sif_potential": "HIGH",
        "confidence": 94.0,
        "urgency_score": 91,
        "evidence_phrase": "curved roof edge of Crude Tank T-301 at 11 meters height; lanyard was unhooked and dangling freely; no static lifeline had been rigged",
        "life_saving_rule": "Working at Height",
        "failed_barrier": "100% Fall Arrest Tie-Off & Engineered Static Lifeline",
        "barrier_status": "FAILED",
        "potential_consequence": "Fatal blunt impact trauma from an 11-meter unprotected fall onto concrete tank containment bund.",
        "ai_explanation": "Working on an unprotected elevated curved tank roof without positive 100% tie-off or edge guardrails in adverse wind conditions.",
        "review_status": "APPROVED",
        "created_offset_days": 5,
    },
    {
        "report_id": "SIF-2026-00129",
        "reporter_id": "USR-006",
        "facility_id": "FAC-JOR-05",
        "location": "Trunkline Section 4, River Crossing RoW",
        "raw_report_text": "During heavy monsoon flooding, an OIL utility vehicle carrying four technicians was dispatched across an unverified causeway with rapid floodwaters reaching the wheel hubs. The vehicle lost traction and slid 2 meters toward a deep gully before the driver managed to reverse out.",
        "language": "English",
        "report_type": "Near Miss",
        "activity": "Journey & Field Logistics",
        "primary_hazard": "Flash Flood Vehicular Rollover / Drowning",
        "precursor_category": "Driving & Journey Management",
        "sif_precursor": "YES",
        "sif_potential": "HIGH",
        "confidence": 91.0,
        "urgency_score": 86,
        "evidence_phrase": "dispatched across an unverified causeway with rapid floodwaters; vehicle lost traction and slid 2 meters toward a deep gully",
        "life_saving_rule": "Driving & Journey Safety",
        "failed_barrier": "Journey Risk Assessment & Adverse Weather Travel Ban",
        "barrier_status": "FAILED",
        "potential_consequence": "Vehicular submergence or rollover into deep flood current resulting in passenger entrapment and drowning.",
        "ai_explanation": "Dispatching personnel into severe unassessed floodwaters violates mandatory Journey Management severe weather restrictions.",
        "review_status": "PENDING",
        "created_offset_days": 6,
    },
    {
        "report_id": "SIF-2026-00130",
        "reporter_id": "USR-007",
        "facility_id": "FAC-RAJ-09",
        "location": "Thermal Steam Injection Well BGW-08",
        "raw_report_text": "While inspecting high-pressure steam distribution lines (180 bar, 310°C), a technician observed that the high-pressure thermal relief valve bypass had been physically wired shut with steel wire to prevent nuisance tripping during cyclic steam injection.",
        "language": "English",
        "report_type": "Unsafe Condition",
        "activity": "Steam Injection Operations",
        "primary_hazard": "Superheated High-Pressure Steam Overpressure Blast",
        "precursor_category": "Bypassing Safety Controls",
        "sif_precursor": "YES",
        "sif_potential": "CRITICAL",
        "confidence": 97.0,
        "urgency_score": 98,
        "evidence_phrase": "thermal relief valve bypass had been physically wired shut with steel wire to prevent nuisance tripping",
        "life_saving_rule": "Bypassing Safety Controls",
        "failed_barrier": "Pressure Relief Device Integrity & Management of Change (MOC)",
        "barrier_status": "FAILED",
        "potential_consequence": "Catastrophic steam piping rupture and explosive superheated flash steam expansion causing fatal thermal burns.",
        "ai_explanation": "Intentional defeat of an overpressure safety relief device on superheated 180-bar steam manifold without authorized MOC.",
        "review_status": "APPROVED",
        "created_offset_days": 7,
    },
    {
        "report_id": "SIF-2026-00131",
        "reporter_id": "USR-009",
        "facility_id": "FAC-KGB-08",
        "location": "Quayside Berth-2, Heavy Crane Pad",
        "raw_report_text": "While offloading a 14-ton subsea Christmas tree manifold from an offshore supply vessel, the primary wire sling slipped on the wet crane hook latch because the safety retention tongue was seized and tied open. The load tilted sharply to 35 degrees before settling onto the quayside bumper.",
        "language": "English",
        "report_type": "Near Miss",
        "activity": "Marine Quayside Cargo Lifting",
        "primary_hazard": "14-Ton Uncontrolled Suspended Heavy Load",
        "precursor_category": "Lifting Operations",
        "sif_precursor": "YES",
        "sif_potential": "CRITICAL",
        "confidence": 96.0,
        "urgency_score": 96,
        "evidence_phrase": "safety retention tongue was seized and tied open; primary wire sling slipped on the wet crane hook; 14-ton subsea Christmas tree",
        "life_saving_rule": "Safe Mechanical Lifting",
        "failed_barrier": "Crane Hook Safety Latch & Pre-Lift Rigging Inspection",
        "barrier_status": "FAILED",
        "potential_consequence": "Dropped 14-ton subsea manifold crushing quayside deck workers or capsizing supply vessel deck rigging.",
        "ai_explanation": "Defeat of critical crane hook safety catch during high-tonnage marine lifting over quayside personnel zone.",
        "review_status": "PENDING",
        "created_offset_days": 8,
    },
    {
        "report_id": "SIF-2026-00132",
        "reporter_id": "USR-010",
        "facility_id": "FAC-BAR-10",
        "location": "Amine Sweetening Unit, Absorber Column C-101",
        "raw_report_text": "Maintenance technician started unbolting an orifice plate flange on the sour gas feed line without checking the bleed needle valve. Trapped sour gas under 22 bar pressure hissed out violently. Technician evacuated the ladder immediately; area H2S beacon flashed red within 15 seconds.",
        "language": "English",
        "report_type": "Incident",
        "activity": "Flange Breaking & Orifice Inspection",
        "primary_hazard": "Toxic Sour Gas Release (H2S Under Pressure)",
        "precursor_category": "Energy Isolation",
        "sif_precursor": "YES",
        "sif_potential": "HIGH",
        "confidence": 95.0,
        "urgency_score": 94,
        "evidence_phrase": "unbolting an orifice plate flange without checking the bleed needle valve; Trapped sour gas under 22 bar pressure hissed out violently",
        "life_saving_rule": "Energy Isolation",
        "failed_barrier": "Bleed Port Verification & First Line Break Checklist",
        "barrier_status": "FAILED",
        "potential_consequence": "Lethal toxic H2S exposure and traumatic projectile impact from unbolted flange plate.",
        "ai_explanation": "Line breaking on pressurized sour gas stream without positive isolation verification or bleed line clearance.",
        "review_status": "APPROVED",
        "created_offset_days": 9,
    },
    {
        "report_id": "SIF-2026-00133",
        "reporter_id": "USR-001",
        "facility_id": "FAC-DUL-01",
        "location": "Central Workshop, Overhead Crane Bay #4",
        "raw_report_text": "Contractor rigger walked directly under a 6-ton electric motor suspended 4 meters in the air by an overhead bridge crane to pick up a dropped wrench. Crane operator had to slam the emergency stop when the motor swayed within 1 meter of the worker.",
        "language": "English",
        "report_type": "Unsafe Act",
        "activity": "Workshop Heavy Fabrication",
        "primary_hazard": "Suspended Overhead Load / Line of Fire",
        "precursor_category": "Line of Fire",
        "sif_precursor": "YES",
        "sif_potential": "HIGH",
        "confidence": 94.0,
        "urgency_score": 89,
        "evidence_phrase": "walked directly under a 6-ton electric motor suspended 4 meters in the air; crane operator had to slam the emergency stop",
        "life_saving_rule": "Line of Fire",
        "failed_barrier": "Exclusion Zone Barricading & Worker Line-of-Fire Discipline",
        "barrier_status": "FAILED",
        "potential_consequence": "Fatal crushing trauma from falling 6-ton suspended electrical machinery.",
        "ai_explanation": "Direct worker entry into the high-hazard drop zone beneath an active suspended load.",
        "review_status": "PENDING",
        "created_offset_days": 10,
    },
]

# Generate additional diverse seed reports to reach 50+ records
EXTRA_TEMPLATES = [
    {
        "facility_id": "FAC-DUL-01",
        "category": "Energy Isolation",
        "rule": "Energy Isolation",
        "hazard": "Stored Electrical Energy (3.3 kV Switchgear)",
        "activity": "Substation Switchgear Maintenance",
        "barrier": "High Voltage Grounding & LOTO Verification",
        "sif": "HIGH",
        "urgency": 90,
        "text": "Electrician opened 3.3 kV breaker cubicle #4 to clean busbars before earth switch had been closed. Test probe revealed incoming feeder was still energized from auxiliary transformer.",
    },
    {
        "facility_id": "FAC-NHK-06",
        "category": "Lifting Operations",
        "rule": "Safe Mechanical Lifting",
        "hazard": "Dropped Tubular Casing Joint (4.5 tons)",
        "activity": "Casing Running Operations",
        "barrier": "Single Joint Elevator Latch Locking Mechanism",
        "sif": "CRITICAL",
        "urgency": 95,
        "text": "During casing running, the single-joint elevator safety pin failed to engage completely. 13-3/8 inch casing joint slipped 0.5m inside the v-door before catching on the slide ramp.",
    },
    {
        "facility_id": "FAC-MOR-03",
        "category": "Confined Space",
        "rule": "Confined Space Entry",
        "hazard": "Hydrocarbon Vapor Accumulation in Sump Pit",
        "activity": "Cellar Pit Sludge Removal",
        "barrier": "Continuous Sump Pit Forced Ventilation",
        "sif": "HIGH",
        "urgency": 89,
        "text": "Two helpers entered a 3-meter deep cellar sump pit to clear clogged suction lines while crude skim was bubbling. Portable multi-gas monitor in pocket alarmed at 24% LEL.",
    },
    {
        "facility_id": "FAC-DIG-02",
        "category": "Working at Height",
        "rule": "Working at Height",
        "hazard": "Fall from Scaffold Platform (7m)",
        "activity": "Cooling Tower Louver Overhaul",
        "barrier": "Complete Scaffold Guardrailing & Green Tagging",
        "sif": "HIGH",
        "urgency": 88,
        "text": "Technician walked onto an incomplete scaffold cantilever board at 7m elevation without top rail or intermediate rail fitted. Scaffold green inspection tag was missing.",
    },
    {
        "facility_id": "FAC-MAK-04",
        "category": "Hot Work",
        "rule": "Hot Work & Ignition Control",
        "hazard": "Grinding Sparks Near Gas Condensate Drain",
        "activity": "Pipe Spool Modification",
        "barrier": "Spark Containment Blanket & Atmospheric Testing",
        "sif": "HIGH",
        "urgency": 87,
        "text": "Mechanical contractor operated an angle grinder 3 meters from open oily water drain without fire blanket or continuous LEL monitoring. Hot slag ignited dry leaves near drain rim.",
    },
    {
        "facility_id": "FAC-JOR-05",
        "category": "Driving & Journey Management",
        "rule": "Driving & Journey Safety",
        "hazard": "Heavy Pipe Hauler Rollover on Narrow Embankment",
        "activity": "Line Pipe Haulage",
        "barrier": "Heavy Haul Route Survey & Convoy Escort Protocol",
        "sif": "HIGH",
        "urgency": 86,
        "text": "Contractor 12-wheel prime mover carrying 8 joints of 24-inch pipe approached soft unpaved shoulder on bund road at excessive speed; right trailer tires sank 30cm.",
    },
]

SEED_ACTIONS = [
    {
        "action_id": "ACT-2026-081",
        "report_id": "SIF-2026-00124",
        "assigned_to": "USR-002",
        "facility_id": "FAC-DIG-02",
        "action_type": "Isolation Audit & LOTO Enforcement",
        "description": "Conduct comprehensive Lockout/Tagout (LOTO) and zero-energy verification audit across all Digboi Train-2 compressor manifolds. Retrain mechanical maintenance contractors on positive bleed valve checks before breaking flanges.",
        "priority": "CRITICAL",
        "status": "In Progress",
        "due_offset_days": 7,
    },
    {
        "action_id": "ACT-2026-082",
        "report_id": "SIF-2026-00125",
        "assigned_to": "USR-004",
        "facility_id": "FAC-NHK-06",
        "action_type": "Equipment Overhaul & NDT Rigging Inspection",
        "description": "Replace all auxiliary air hoist wire ropes on Rig NHK-42 with certified third-party magnetic particle tested slings. Re-establish physical red exclusion line on rig floor rotary perimeter during tubular hoisting.",
        "priority": "CRITICAL",
        "status": "Open",
        "due_offset_days": 4,
    },
    {
        "action_id": "ACT-2026-083",
        "report_id": "SIF-2026-00126",
        "assigned_to": "USR-003",
        "facility_id": "FAC-MOR-03",
        "action_type": "CAPA & Standby System Overhaul",
        "description": "Suspend contractor vendor entry permit until formal inquiry concludes. Install interlocked mechanical entry barriers on all Moran GGS separators requiring physical dual-signature atmospheric sign-off prior to hatch unlock.",
        "priority": "CRITICAL",
        "status": "Open",
        "due_offset_days": 2,
    },
    {
        "action_id": "ACT-2026-084",
        "report_id": "SIF-2026-00127",
        "assigned_to": "USR-005",
        "facility_id": "FAC-MAK-04",
        "action_type": "Hot Work Habitat Compliance Audit",
        "description": "Inspect and verify positive-pressure hot work enclosures on all Makum DCS flare headers. Enforce mandatory continuous 4-gas monitoring within 10 meters of any live hydrocarbon line break.",
        "priority": "HIGH",
        "status": "In Progress",
        "due_offset_days": 6,
    },
    {
        "action_id": "ACT-2026-085",
        "report_id": "SIF-2026-00128",
        "assigned_to": "USR-008",
        "facility_id": "FAC-KUM-07",
        "action_type": "Tank Dome Lifeline Retrofit",
        "description": "Install stainless steel 316 continuous static lifelines across all Kumchai crude storage tank roofs. Mandate dual-lanyard shock-absorbing harness tie-off before issuing tank roof access permits.",
        "priority": "HIGH",
        "status": "Completed",
        "due_offset_days": -2,
    },
    {
        "action_id": "ACT-2026-086",
        "report_id": "SIF-2026-00129",
        "assigned_to": "USR-006",
        "facility_id": "FAC-JOR-05",
        "action_type": "Monsoon Fleet Dispatch Ban Protocol",
        "description": "Implement automated SMS severe weather dispatch hold for all Jorhat pipeline survey vehicles during active Brahmaputra river crossing flood advisories.",
        "priority": "MEDIUM",
        "status": "Completed",
        "due_offset_days": -5,
    },
    {
        "action_id": "ACT-2026-087",
        "report_id": "SIF-2026-00130",
        "assigned_to": "USR-007",
        "facility_id": "FAC-RAJ-09",
        "action_type": "Overpressure Relief Valve Tamper Audit",
        "description": "Inspect all 180-bar steam relief valves across Rajasthan thermal project. Install tamper-evident numbered car-seals on all PSV isolation bypasses and file formal safety violation report.",
        "priority": "CRITICAL",
        "status": "In Progress",
        "due_offset_days": 3,
    },
    {
        "action_id": "ACT-2026-088",
        "report_id": "SIF-2026-00131",
        "assigned_to": "USR-009",
        "facility_id": "FAC-KGB-08",
        "action_type": "Marine Quayside Crane Latch Overhaul",
        "description": "Replace seized crane hook spring-loaded safety latches across all Kakinada quayside heavy cranes. Issue quayside safety alert on load rigging inspection.",
        "priority": "CRITICAL",
        "status": "Open",
        "due_offset_days": 1,
    },
    {
        "action_id": "ACT-2026-089",
        "report_id": "SIF-2026-00132",
        "assigned_to": "USR-010",
        "facility_id": "FAC-BAR-10",
        "action_type": "Sour Gas Flange Line Breaking Procedure",
        "description": "Mandate positive zero-pressure verification and SCBA airpack standby on all Barekuri GGS sour gas line breaking tasks.",
        "priority": "HIGH",
        "status": "Overdue",
        "due_offset_days": -1,
    },
    {
        "action_id": "ACT-2026-090",
        "report_id": "SIF-2026-00133",
        "assigned_to": "USR-001",
        "facility_id": "FAC-DUL-01",
        "action_type": "Overhead Crane Red Exclusion Zone",
        "description": "Paint high-visibility optical red floor exclusion perimeters beneath all Duliajan workshop overhead cranes. Install acoustic warning beacons during bridge traverse.",
        "priority": "MEDIUM",
        "status": "In Progress",
        "due_offset_days": 8,
    },
]


async def seed_database() -> None:
    print("🚀 Initializing SIFT database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    now = datetime.now(timezone.utc)
    vector_store = get_vector_store()
    embedding_provider = get_embedding_provider()

    async with AsyncSessionLocal() as session:
        print("🌱 Seeding Users...")
        for u in SEED_USERS:
            existing = (await session.execute(select(User).where(User.user_id == u["user_id"]))).scalars().first()
            if not existing:
                user = User(
                    user_id=u["user_id"],
                    name=u["name"],
                    email=u["email"],
                    role=u["role"],
                    title=u["title"],
                    facility_id=u["facility_id"],
                    contact_number=u["contact_number"],
                    avatar=u["avatar"],
                    active=True,
                )
                session.add(user)
        await session.commit()

        print("🌱 Seeding Facilities...")
        for f in SEED_FACILITIES:
            existing = (await session.execute(select(Facility).where(Facility.facility_id == f["facility_id"]))).scalars().first()
            if not existing:
                fac = Facility(
                    facility_id=f["facility_id"],
                    name=f["name"],
                    short_name=f["short_name"],
                    region=f["region"],
                    type=f["type"],
                    location_description=f["location_description"],
                    latitude=f["latitude"],
                    longitude=f["longitude"],
                    active_personnel=f["active_personnel"],
                    manager=f["manager"],
                    active=True,
                )
                session.add(fac)
        await session.commit()

        print("🌱 Seeding Safety Reports & Barrier Assessments...")
        # 1. Add core curated reports
        report_objs = []
        for r in SEED_REPORTS:
            created_at = now - timedelta(days=r["created_offset_days"])
            rep = SafetyReport(
                report_id=r["report_id"],
                reporter_id=r["reporter_id"],
                facility_id=r["facility_id"],
                location=r["location"],
                raw_report_text=r["raw_report_text"],
                language=r["language"],
                report_type=r["report_type"],
                activity=r["activity"],
                potential_consequence=r["potential_consequence"],
                ai_sif_potential=r["sif_potential"],
                ai_sif_precursor=r["sif_precursor"],
                ai_confidence=r["confidence"],
                ai_urgency_score=r["urgency_score"],
                ai_primary_hazard=r["primary_hazard"],
                ai_precursor_category=r["precursor_category"],
                ai_life_saving_rule=r["life_saving_rule"],
                ai_failed_barrier=r["failed_barrier"],
                ai_barrier_status=r["barrier_status"],
                ai_evidence_phrase=r["evidence_phrase"],
                ai_explanation=r["ai_explanation"],
                review_status=r["review_status"],
                created_at=created_at,
                updated_at=created_at,
            )
            session.add(rep)
            report_objs.append(rep)

        # 2. Add extra synthetic reports across all facilities to reach 52 total reports
        report_counter = 134
        for i in range(42):
            tmpl = EXTRA_TEMPLATES[i % len(EXTRA_TEMPLATES)]
            fac = SEED_FACILITIES[i % len(SEED_FACILITIES)]
            user = SEED_USERS[i % len(SEED_USERS)]
            rep_id = f"SIF-2026-00{str(report_counter).zfill(3)}"
            report_counter += 1

            days_ago = (i * 2) % 45 + 1
            created_at = now - timedelta(days=days_ago)

            rep = SafetyReport(
                report_id=rep_id,
                reporter_id=user["user_id"],
                facility_id=fac["facility_id"],
                location=f"{fac['short_name']}, Sector-{str(i % 5 + 1)}",
                raw_report_text=tmpl["text"],
                language="English",
                report_type="Unsafe Act" if i % 3 == 0 else ("Near Miss" if i % 3 == 1 else "Unsafe Condition"),
                activity=tmpl["activity"],
                potential_consequence=f"Catastrophic failure mode in {tmpl['category']} resulting in acute SIF potential.",
                ai_sif_potential=tmpl["sif"],
                ai_sif_precursor="YES",
                ai_confidence=float(89 + (i % 9)),
                ai_urgency_score=int(tmpl["urgency"] - (i % 6)),
                ai_primary_hazard=tmpl["hazard"],
                ai_precursor_category=tmpl["category"],
                ai_life_saving_rule=tmpl["rule"],
                ai_failed_barrier=tmpl["barrier"],
                ai_barrier_status="FAILED",
                ai_evidence_phrase=tmpl["text"][:60],
                ai_explanation=f"Demonstrates non-compliance in {tmpl['category']} with high potential fatality exposure.",
                review_status="APPROVED" if i % 2 == 0 else "PENDING",
                created_at=created_at,
                updated_at=created_at,
            )
            session.add(rep)
            report_objs.append(rep)

        await session.commit()

        # 3. Add Barrier Assessments and Vector References
        print("🌱 Seeding Barrier Assessments & Vector References...")
        for rep in report_objs:
            barrier = BarrierAssessment(
                report_id=rep.report_id,
                failed_barrier=rep.ai_failed_barrier or "Procedural Verification Safeguard",
                barrier_status=rep.ai_barrier_status or "FAILED",
                life_saving_rule=rep.ai_life_saving_rule,
                description=f"Primary barrier failure diagnosed by SIFT NLP engine: {rep.ai_failed_barrier}",
                created_at=rep.created_at,
                updated_at=rep.created_at,
            )
            session.add(barrier)

            # Vector embedding index
            try:
                vec = await embedding_provider.embed_text(rep.raw_report_text)
                await vector_store.upsert(
                    VectorRecord(
                        id=rep.report_id,
                        values=vec,
                        metadata={
                            "report_id": rep.report_id,
                            "facility_id": rep.facility_id,
                            "precursor_category": rep.ai_precursor_category,
                            "life_saving_rule": rep.ai_life_saving_rule,
                            "sif_potential": rep.ai_sif_potential,
                            "primary_hazard": rep.ai_primary_hazard,
                        },
                    )
                )
                vec_ref = ReportVectorReference(
                    report_id=rep.report_id,
                    vector_id=rep.report_id,
                    embedding_model="sift-dense-embed-v1",
                    dimension=len(vec),
                    indexed_at=rep.created_at,
                )
                session.add(vec_ref)
            except Exception:
                pass

        await session.commit()

        # 4. Add Actions
        print("🌱 Seeding CAPA Action Items...")
        for a in SEED_ACTIONS:
            due_date = now + timedelta(days=a["due_offset_days"])
            action = ActionItem(
                action_id=a["action_id"],
                report_id=a["report_id"],
                assigned_to=a["assigned_to"],
                facility_id=a["facility_id"],
                action_type=a["action_type"],
                description=a["description"],
                priority=a["priority"],
                status=a["status"],
                due_date=due_date,
                created_at=now - timedelta(days=5),
                updated_at=now - timedelta(days=5),
            )
            session.add(action)

        # Generate additional action items to reach 32 actions
        for i in range(22):
            rep = report_objs[i % len(report_objs)]
            user = SEED_USERS[i % len(SEED_USERS)]
            fac = SEED_FACILITIES[i % len(SEED_FACILITIES)]
            due = now + timedelta(days=(i * 3) - 10)
            status_val = ActionStatus.COMPLETED.value if i % 4 == 0 else (ActionStatus.OVERDUE.value if due < now else ActionStatus.IN_PROGRESS.value)

            act = ActionItem(
                action_id=f"ACT-2026-{str(91 + i).zfill(3)}",
                report_id=rep.report_id,
                assigned_to=user["user_id"],
                facility_id=fac["facility_id"],
                action_type=f"Engineering Control Audit & Safeguard Verification #{i+1}",
                description=f"Inspect and remediate safety barrier vulnerabilities associated with {rep.ai_primary_hazard} at {fac['short_name']}.",
                priority=ActionPriority.HIGH.value if i % 2 == 0 else ActionPriority.CRITICAL.value,
                status=status_val,
                due_date=due,
                completed_at=now if status_val == ActionStatus.COMPLETED.value else None,
                created_at=now - timedelta(days=12),
                updated_at=now - timedelta(days=2),
            )
            session.add(act)

        await session.commit()

    print("✅ Database seeding completed successfully! Populated:")
    print(f"   • {len(SEED_USERS)} Users")
    print(f"   • {len(SEED_FACILITIES)} Facilities")
    print(f"   • {len(report_objs)} Safety Reports & Barrier Assessments")
    print(f"   • {len(SEED_ACTIONS) + 22} CAPA Actions")


if __name__ == "__main__":
    asyncio.run(seed_database())
