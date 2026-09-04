# SIFT Canonical Safety Intelligence Taxonomy

**Taxonomy Version:** 1.0  
**Effective Date:** 2026-08-30  
**Authoritative Scope:** Dataset Annotation, Machine Learning Label Spaces, UI Presentation  

---

## 1. Governance & Versioning Principle

Every annotated record, model inference result, and API payload in SIFT is pinned to a strict taxonomy version:
`taxonomy_version = "1.0"`

If categories, rules, or barrier definitions are added or modified in the future, the taxonomy version will increment according to SemVer (e.g. `1.1` for backwards-compatible category additions, `2.0` for structural changes).

---

## 2. SIF Potential Taxonomy (TASK-001)

> [!IMPORTANT]
> **The Critical Distinction: Potential vs. Actual Injury**  
> SIF Potential measures the **capacity of an incident, near miss, or unsafe condition to cause a Serious Injury or Fatality**, independent of the historical outcome.  
> An event with **zero physical injuries** (e.g. a 3.2-ton drill collar falling across the rig floor, narrowly missing workers) must be classified as **CRITICAL SIF Potential**.

| Level | Canonical Code | Definition | Energy / Barrier Criterion |
| :--- | :--- | :--- | :--- |
| **CRITICAL** | `CRITICAL` | Imminent, acute potential for a fatal outcome or multiple catastrophic fatalities. | High-energy hazard released or uncontained in active worker zone; zero functioning physical barriers. |
| **HIGH** | `HIGH` | High probability of severe life-altering injury or single fatality if circumstances varied slightly. | High-energy hazard present with compromised/degraded secondary barrier, or single point of failure away from fatality. |
| **MEDIUM** | `MEDIUM` | Potential for significant lost-time injury (LTI), reversible trauma, or localized equipment damage; unlikely to be fatal. | Medium-energy hazard present; administrative or basic physical barriers partially arrested the release. |
| **LOW** | `LOW` | Minor first-aid case, minor sprain/abrasion, or low-energy procedural deviation. | Low-energy hazard; existing barriers are substantially intact. |
| **NON-SIF** | `NON-SIF` | Routine safety observation, housekeeping, ergonomic observation, or administrative anomaly with zero serious physical consequence. | Zero high-energy hazard exposure. |

---

## 3. SIF Precursor Concept (TASK-002)

### SIF Potential vs. SIF Precursor

- **SIF Potential:** The **magnitude of consequence severity** that the scenario could realistically generate.
- **SIF Precursor:** The **observable condition, behavior, or barrier failure** that creates the exposure pathway to a high-energy hazard.

### SIF Precursor Canonical Values:
1. `YES`: A high-energy hazard was present in the absence of a direct, functioning barrier (or where the barrier failed).
2. `NO`: No unmitigated high-energy hazard pathway existed.
3. `POTENTIAL`: Ambiguous narrative requiring further supervisory investigation to confirm energy state or barrier presence.

---

## 4. SIF Precursor Categories (TASK-003)

### Multi-Label Architecture
A safety observation may legitimately involve multiple simultaneous precursor mechanisms (for example, cleaning an enclosed vessel with 35 bar pressurized supply lines involves both **Confined Space** and **Energy Isolation**).

To prevent information loss, SIFT supports:
- `primary_precursor`: The dominant physical energy mechanism.
- `secondary_precursors`: Array of secondary concurrent mechanisms.

| Precursor Category | Code | Description & Trigger Criteria |
| :--- | :--- | :--- |
| **Energy Isolation** | `ENERGY_ISOLATION` | Hazardous energy (pressure, hydraulic, chemical, mechanical) servicing without verified LOTO, zero-energy check, or physical blind. |
| **Confined Space** | `CONFINED_SPACE` | Entry into vessels, separators, tanks, or trenches with toxic atmosphere, H2S, O2 deficiency, or engulfment hazards. |
| **Line of Fire** | `LINE_OF_FIRE` | Personnel positioned in the trajectory of moving machinery, under suspended loads, or near pressurized whip lines. |
| **Working at Height** | `WORKING_AT_HEIGHT` | Unprotected work at elevations >2m, missing 100% tie-off, unhooked lanyard, or non-compliant scaffolding. |
| **Hot Work** | `HOT_WORK` | Welding, burning, grinding, or open flames within classified hydrocarbon process areas without verified gas clearance. |
| **Lifting Operations** | `LIFTING_OPERATIONS` | Crane, hoist, winch, or rigging operations with damaged slings, overloaded capacity, or missing exclusion zones. |
| **Driving & Journey Management** | `DRIVING_SAFETY` | Heavy transport, rough terrain vehicle operations, lack of seatbelts, speeding, or uninspected vehicle equipment. |
| **Bypassing Safety Controls** | `BYPASSING_SAFEGUARDS` | Intentional defeat, bridging, or overriding of ESD valves, interlocks, PRVs, or safety alarms without formal MOC. |
| **Toxic Gas & Chemical Exposure** | `TOXIC_GAS_EXPOSURE` | Exposure to H2S gas, hazardous process chemicals, caustic muds, or solvent vapors. |
| **Process Safety** | `PROCESS_SAFETY` | Loss of primary containment (LOPC), hydrocarbon leaks, flange integrity failure, or overpressure events. |
| **Procedural Safety** | `PROCEDURAL_SAFETY` | Failure to obtain Permit to Work (PTW), missing Tool Box Talk (TBT), or unauthorized operational deviations. |
| **Other** | `OTHER` | Precursor hazard not covered by the standard taxonomy categories. |

---

## 5. Primary Hazard Taxonomy (TASK-004)

Standardized high-energy physical and chemical hazard classifications:

1. `Stored / Pressurized Hydrocarbon Energy` (High-pressure gas, liquid hydrocarbons, accumulator pressure)
2. `Toxic Gas / Asphyxiation (H2S & O2 Deficiency)` (Hydrogen sulfide, nitrogen purge, enclosed oxygen depletion)
3. `Dropped Heavy Object / Line of Fire` (Tubulars, derrick tools, suspended loads, crane rigging)
4. `Unprotected Fall from Elevated Height (>2m)` (Scaffold edges, tank roofs, monkey board, ladders)
5. `Ignition of Hydrocarbon Vapor Cloud` (Hot work sparks, unrated electrical equipment, static discharge)
6. `Electrical Arc Flash & Energized Circuits` (High-voltage switchgear, damaged trailing cables)
7. `Rotating Machinery & Heavy Mechanical Pinch` (Rotary table, top drive, mud pump pulleys, winches)
8. `Corrosive / Hazardous Chemical Splash` (Acidizing fluids, caustic drilling mud additives)
9. `Vehicle Rollover & Heavy Transport Collision` (Bowser trucks, crew transport on wet unpaved rig roads)
10. `Trench & Excavation Wall Collapse` (Pipeline trenching without shoring or battering)
11. `Operational Hazard Exposure` (General operational industrial hazard)
12. `Other`

---

## 6. Operational Activity Taxonomy (TASK-005)

Standardized operational activity context:

1. `Maintenance` (Mechanical, electrical, instrumentation servicing and repair)
2. `Drilling Operations` (Tripping pipe, making connections, drilling ahead, casing running)
3. `Well Intervention` (Coiled tubing, wireline, snubbing, hydraulic workover)
4. `Lifting & Rigging` (Crane lifts, hoist operations, equipment staging)
5. `Vessel Cleaning & Desanding` (Separator scraping, crude tank de-sludging)
6. `Working at Height` (Painting tank roofs, derrick maintenance, scaffold erection)
7. `Hot Work & Welding` (Structural welding, pipeline tie-ins, grinding)
8. `Pipeline Pigging & Transport` (Launcher/receiver operations, pipeline right-of-way inspection)
9. `Plant Operations & Header Sampling` (Gas compressor monitoring, GGS manifold switching)
10. `Electrical Substation Servicing` (Transformer maintenance, breaker switching)
11. `Civil Construction & Excavation` (Road building, bund wall construction, trenching)
12. `Other`

---

## 7. IOGP Life-Saving Rules Taxonomy (TASK-006)

*Note on Authority: The application utilizes standardized Life-Saving Rules aligned with international IOGP (International Association of Oil & Gas Producers) safety frameworks as adopted for Oil India Limited operations.*

| Rule ID | Rule Name | Description | Key Safeguards |
| :--- | :--- | :--- | :--- |
| `LSR-01` | **Energy Isolation** | Verify isolation and zero energy before work begins. | Apply Lockout/Tagout, bleed pressure, verify zero state, test voltage. |
| `LSR-02` | **Confined Space Entry** | Obtain authorization and test atmosphere before entering. | Multi-gas testing (LEL, O2, H2S), forced ventilation, continuous standby watch. |
| `LSR-03` | **Line of Fire** | Keep yourself and others out of the line of fire. | Enforce exclusion zones, stay clear of suspended loads, secure whip checks. |
| `LSR-04` | **Safe Mechanical Lifting** | Plan lifting operations and control the area. | Verified rigging gear, certified crane operator, approved lift plan. |
| `LSR-05` | **Working at Height** | Protect yourself against a fall when working at height. | 100% continuous tie-off, inspected safety harness, engineered static lifeline. |
| `LSR-06` | **Hot Work & Ignition Control** | Control flammables and ignition sources. | Continuous explosimeter testing, hot work permit, positive-pressure habitat. |
| `LSR-07` | **Safe Driving & Journey Management** | Follow safe driving rules and wear seatbelts. | Journey management plan, speed limits, vehicle pre-use inspection. |
| `LSR-08` | **Bypassing Safety Controls** | Obtain authorization before overriding safety controls. | Formal MOC authorization, risk assessment, time-limited bypass register. |
| `LSR-09` | **Toxic Gas Protection (H2S)** | Verify atmospheric clearance and wear personal monitors. | Personal H2S detector, escape breathing apparatus (EEBD), buddy system. |
| `LSR-10` | **Work Authorization & PTW** | Work with a valid Permit to Work when required. | Job safety analysis (JSA), approved PTW, tool box talk with crew sign-off. |

---

## 8. Safety Barrier Taxonomy & Status (TASK-007 & TASK-008)

### Barrier Hierarchy Categories:
1. **Engineering / Physical Barrier:** Blinds, PRVs, interlocks, scaffolding handrails, physical barricades, ESD systems.
2. **Administrative / Procedural Barrier:** Permit to Work (PTW), Isolation Certificates, Gas Test Certificates, Lifting Plans.
3. **Behavioral / Last Line of Defense (PPE):** Safety harnesses, personal H2S detectors, respirators, flame-resistant clothing (FRC).

### Barrier Status Definitions:

| Status | Code | Definition | Rule for Application |
| :--- | :--- | :--- | :--- |
| **FAILED** | `FAILED` | The barrier was required and present/specified, but physically failed, broke, or was completely bypassed/violated. | Explicit text evidence of failure (e.g. wire rope snapped, isolation not done). |
| **WEAK** | `WEAK` | The barrier existed but was degraded, incomplete, or partially effective. | Text evidence of partial implementation (e.g. gas tested 4 hours ago, harness on but unhooked). |
| **EFFECTIVE** | `EFFECTIVE` | The barrier functioned as engineered and successfully prevented the incident escalation. | Text states barrier stopped the hazard (e.g. PRV lifted cleanly, whip check caught hose). |
| **UNKNOWN** | `UNKNOWN` | The narrative lacks sufficient detail to determine barrier condition. | No text evidence regarding barrier performance. |
