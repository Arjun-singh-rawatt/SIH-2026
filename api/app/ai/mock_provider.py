"""Deterministic rule-based Mock AI Provider for SIFT NLP pipeline."""

import re
from typing import List, Tuple
from app.schemas.analysis import AnalyzeRequest, ReportAnalysisResult
from app.utils.enums import SIFPotential, SIFPrecursor, BarrierStatus


class MockAIProvider:
    """Deterministic domain rule-based AI NLP provider for Oil & Gas safety observations."""

    async def analyze_report(self, request: AnalyzeRequest) -> ReportAnalysisResult:
        text = request.report_text.lower()
        
        # Default fallback classification
        sif_potential = SIFPotential.MEDIUM.value
        sif_precursor = SIFPrecursor.YES.value
        confidence = 88.0
        urgency_score = 65
        precursor_category = "Procedural Safety"
        primary_hazard = "Operational Hazard Exposure"
        life_saving_rule = "Bypassing Safety Controls"
        failed_barrier = "Task Risk Assessment & Procedural Compliance"
        barrier_status = BarrierStatus.FAILED.value
        potential_consequence = "Potential localized injury or equipment damage due to substandard control enforcement."
        ai_explanation = (
            "The safety observation demonstrates procedural non-compliance during operational activities. "
            "Barrier effectiveness was compromised, warranting supervisory verification."
        )
        evidence_phrases: List[str] = []

        # 1. Energy Isolation / Stored Pressure
        if any(k in text for k in ["isolation", "loto", "lockout", "35 bar", "pressurized", "pressure gauge", "flange seal", "bleed"]):
            sif_potential = SIFPotential.HIGH.value
            if any(k in text for k in ["35 bar", "needle vibrating", "blew out", "high pressure", "pressurized line"]):
                sif_potential = SIFPotential.CRITICAL.value
                urgency_score = 94
            else:
                urgency_score = 88
            confidence = 95.0
            precursor_category = "Energy Isolation"
            primary_hazard = "Stored / Pressurized Hydrocarbon Energy"
            life_saving_rule = "Energy Isolation"
            failed_barrier = "Zero Energy Verification & Isolation Certificate"
            potential_consequence = "Catastrophic release of pressurized hydrocarbon gas resulting in high-velocity shrapnel impact and potential fatal blast/fire."
            ai_explanation = (
                "The activity involved breaking containment or servicing equipment on a pressurized hydrocarbon system "
                "without positive isolation or zero-energy verification. Failure of line containment carries high potential for fatal blast impact."
            )
            for match in ["without proper isolation", "still pressurized", "loosening bolts", "pressure gauge needle vibrating", "flange seal"]:
                if match in text:
                    evidence_phrases.append(match)

        # 2. Confined Space & Toxic Gases (H2S / Oxygen Deficiency)
        elif any(k in text for k in ["confined space", "manway", "separator", "vessel", "h2s", "oxygen", "ppm", "asphyxiation", "tank entry"]):
            sif_potential = SIFPotential.CRITICAL.value
            confidence = 97.5
            urgency_score = 98
            precursor_category = "Confined Space"
            primary_hazard = "Toxic Gas / Asphyxiation (H2S & O2 Deficiency)"
            life_saving_rule = "Confined Space Entry"
            failed_barrier = "Pre-Entry Multi-Gas Atmospheric Testing & Standby Attendant"
            potential_consequence = "Rapid toxic H2S knockdown or fatal hypoxic asphyxiation inside enclosed hydrocarbon vessel."
            ai_explanation = (
                "Personnel entered an enclosed hydrocarbon processing vessel without verified atmospheric gas clearance "
                "and without continuous forced ventilation or stationed standby watchman. Acute risk of immediate fatal asphyxiation."
            )
            for match in ["without conducting pre-entry atmospheric gas testing", "42 ppm h2s", "16.4% oxygen", "standby observer was absent", "opened the manway"]:
                if match in text:
                    evidence_phrases.append(match)

        # 3. Lifting Operations / Line of Fire / Dropped Objects
        elif any(k in text for k in ["hoist", "crane", "rig floor", "wire rope", "snapped", "suspended load", "sling", "collar", "line of fire"]):
            sif_potential = SIFPotential.CRITICAL.value
            confidence = 96.0
            urgency_score = 96
            precursor_category = "Lifting Operations"
            primary_hazard = "Dropped Heavy Object / Line of Fire"
            life_saving_rule = "Safe Mechanical Lifting"
            failed_barrier = "Rigging Equipment Integrity & Exclusion Zone Enforcement"
            potential_consequence = "Direct fatal crushing or blunt trauma impact from uncontrolled suspended heavy load swinging across active work zone."
            ai_explanation = (
                "Critical lifting equipment failed under mechanical load while personnel were positioned in the line of fire. "
                "The lack of enforced exclusion zone barricading placed workers at imminent risk of fatal impact."
            )
            for match in ["wire rope snapped", "3.2-ton", "line of fire", "suspended drill collar", "narrowly missing two roughnecks"]:
                if match in text:
                    evidence_phrases.append(match)

        # 4. Working at Height / Fall Arrest
        elif any(k in text for k in ["height", "harness", "lanyard", "unhooked", "scaffold", "tank dome", "fall", "11m", "10m", "roof edge"]):
            sif_potential = SIFPotential.HIGH.value
            confidence = 93.0
            urgency_score = 91
            precursor_category = "Working at Height"
            primary_hazard = "Unprotected Fall from Elevated Height (>2m)"
            life_saving_rule = "Working at Height"
            failed_barrier = "100% Continuous Fall Arrest Tie-Off & Static Lifeline"
            potential_consequence = "Fatal blunt force trauma resulting from an unprotected fall from height onto steel substructure."
            ai_explanation = (
                "Work at elevated height was conducted without positive 100% tie-off or engineered anchor lifelines. "
                "Any slip or gust of wind at elevated height carries severe fatality potential."
            )
            for match in ["lanyard was unhooked", "11 meters height", "no static lifeline", "scraping rust on the curved roof edge"]:
                if match in text:
                    evidence_phrases.append(match)

        # 5. Hot Work / Flammable Atmosphere
        elif any(k in text for k in ["hot work", "welding", "grinding", "spark", "gas leak", "hydrocarbon weep", "explosive", "lel"]):
            sif_potential = SIFPotential.HIGH.value
            confidence = 94.0
            urgency_score = 89
            precursor_category = "Hot Work"
            primary_hazard = "Ignition of Hydrocarbon Vapor Cloud"
            life_saving_rule = "Hot Work & Ignition Control"
            failed_barrier = "Continuous LEL Explosimeter Monitoring & Habitat Positive Pressure"
            potential_consequence = "Vapor cloud ignition resulting in flash fire or explosion across active processing area."
            ai_explanation = (
                "Hot work ignition source was introduced within hazardous hydrocarbon zone without adequate gas testing or habitat isolation."
            )
            for match in ["welding near", "active hydrocarbon", "sparks flying", "without gas detector"]:
                if match in text:
                    evidence_phrases.append(match)

        # Ensure evidence phrases list is populated
        if not evidence_phrases:
            # Fallback regex extraction of key clauses
            sentences = [s.strip() for s in re.split(r'[,.;]', request.report_text) if len(s.strip()) > 10]
            evidence_phrases = sentences[:3] if sentences else [request.report_text[:80]]

        evidence_phrase_str = "; ".join(evidence_phrases)

        return ReportAnalysisResult(
            sif_potential=sif_potential,
            sif_precursor=sif_precursor,
            confidence=confidence,
            urgency_score=urgency_score,
            precursor_category=precursor_category,
            activity=request.activity or "Operational Maintenance",
            primary_hazard=primary_hazard,
            life_saving_rule=life_saving_rule,
            failed_barrier=failed_barrier,
            barrier_status=barrier_status,
            potential_consequence=potential_consequence,
            evidence_phrase=evidence_phrase_str,
            evidence_phrases=evidence_phrases,
            ai_explanation=ai_explanation,
        )
