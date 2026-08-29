/**
 * Mock NLP Classification Engine for SIFT
 * In production, this module will be replaced by a REST API call to a FastAPI/Python backend
 * running fine-tuned RoBERTa/LLM classifiers with vector embeddings.
 */

export function analyzeSafetyReport(rawText, metadata = {}) {
  const text = (rawText || '').toLowerCase();
  
  // Default non-SIF baseline
  let classification = {
    sifPotential: 'NON-SIF',
    sifPrecursor: 'NO',
    confidence: 85,
    urgencyScore: 18,
    activity: metadata.activity || 'General Operations',
    primaryHazard: 'Low-Energy Physical Hazard',
    precursorCategory: 'Process Safety',
    lifeSavingRule: 'System & Asset Integrity',
    failedBarrier: 'Routine Operating Procedure',
    barrierStatus: 'EFFECTIVE',
    potentialConsequence: 'Minor localized disturbance with minimal personnel injury potential.',
    evidencePhrases: [],
    aiExplanation: 'The reported narrative describes low-energy operational activity without exposure to high fatal precursors or uncontained fatal energies.',
  };

  // 1. Confined Space
  if (text.includes('confined') || text.includes('vessel') || text.includes('manway') || text.includes('tank entry') || text.includes('asphyxi') || text.includes('separator v-')) {
    const hasH2S = text.includes('h2s') || text.includes('ppm') || text.includes('gas') || text.includes('toxic');
    const hasNoTest = text.includes('without') || text.includes('no test') || text.includes('failed') || text.includes('absent');
    
    classification = {
      sifPotential: 'CRITICAL',
      sifPrecursor: 'YES',
      confidence: 96,
      urgencyScore: hasH2S ? 98 : 91,
      activity: metadata.activity || 'Confined Space Cleaning & Entry',
      primaryHazard: hasH2S ? 'Toxic Gas Accumulation / Lethal Asphyxiation (H2S)' : 'Oxygen Deficient Atmosphere in Enclosed Vessel',
      precursorCategory: 'Confined Space',
      lifeSavingRule: 'Confined Space Entry',
      failedBarrier: 'Atmospheric Multi-Gas Pre-testing & Dedicated Standby Watchman',
      barrierStatus: 'FAILED',
      potentialConsequence: 'Rapid toxic knockdown or fatal asphyxiation to entrants inside unventilated enclosed vessel.',
      evidencePhrases: extractPhrases(rawText, ['confined space', 'vessel', 'manway', 'gas test', 'h2s', 'oxygen', 'ventilation', 'standby', 'ppm']),
      aiExplanation: 'The report indicates entry into an enclosed vessel without certified multi-gas atmospheric testing and absent standby rescue monitoring, presenting direct fatality risk from toxic inhalation or oxygen deficiency.',
    };
  }
  // 2. Energy Isolation / Pressurized Systems / Steam
  else if (text.includes('isolation') || text.includes('lockout') || text.includes('loto') || text.includes('pressur') || text.includes('bar ') || text.includes('psi') || text.includes('bleed') || text.includes('valve') || text.includes('steam')) {
    const isCritical = text.includes('steam') || text.includes('bar') || text.includes('psi') || text.includes('without isolation');
    
    classification = {
      sifPotential: isCritical ? 'CRITICAL' : 'HIGH',
      sifPrecursor: 'YES',
      confidence: 94,
      urgencyScore: isCritical ? 94 : 86,
      activity: metadata.activity || 'Pressurized Line Maintenance & Valve Servicing',
      primaryHazard: text.includes('steam') ? 'Superheated High-Pressure Steam (Thermal Scald & Blast)' : 'Stored Pressurized Hydrocarbon Energy Release',
      precursorCategory: 'Energy Isolation',
      lifeSavingRule: 'Energy Isolation',
      failedBarrier: 'Zero Energy Verification & Double Block and Bleed (DBB) Protocol',
      barrierStatus: 'FAILED',
      potentialConsequence: 'High-velocity fluid/gas release or extreme thermal scalds resulting in fatal bodily trauma upon containment breach.',
      evidencePhrases: extractPhrases(rawText, ['isolation', 'pressurized', 'bleed', 'valve', 'bar', 'psi', 'steam', 'flange', 'loto', 'loosening']),
      aiExplanation: 'Containment hardware or valves were unbolted or manipulated without verified zero-energy state or positive physical spading on a pressurized hydrocarbon/thermal line.',
    };
  }
  // 3. Working at Height
  else if (text.includes('height') || text.includes('scaffold') || text.includes('fall') || text.includes('lanyard') || text.includes('harness') || text.includes('mast') || text.includes('elevation') || text.includes('ladder') || text.includes('roof')) {
    const isExtremeHeight = text.includes('mast') || text.includes('28m') || text.includes('11m') || text.includes('34m') || text.includes('unhook');
    
    classification = {
      sifPotential: isExtremeHeight ? 'CRITICAL' : 'HIGH',
      sifPrecursor: 'YES',
      confidence: 95,
      urgencyScore: isExtremeHeight ? 97 : 85,
      activity: metadata.activity || 'Elevated Structure Maintenance / Derrick Work',
      primaryHazard: 'Catastrophic Fall from Height (>1.8m Elevation)',
      precursorCategory: 'Working at Height',
      lifeSavingRule: 'Working at Height',
      failedBarrier: '100% Continuous Fall Protection Tie-off & Engineered Anchor Lifeline',
      barrierStatus: 'FAILED',
      potentialConsequence: 'Fatal blunt impact from elevation fall due to missing or detached primary fall arrest harness anchor.',
      evidencePhrases: extractPhrases(rawText, ['height', 'scaffold', 'lanyard', 'harness', 'unhooked', 'fall', 'elevation', 'mast', 'ladder', 'roof']),
      aiExplanation: 'Personnel exposed to elevated fall hazard with absent, unhooked, or compromised fall protection equipment.',
    };
  }
  // 4. Lifting Operations / Crane / Rigging
  else if (text.includes('crane') || text.includes('sling') || text.includes('lift') || text.includes('hoist') || text.includes('rigging') || text.includes('suspended') || text.includes('shackle') || text.includes('tubular')) {
    classification = {
      sifPotential: 'HIGH',
      sifPrecursor: 'YES',
      confidence: 93,
      urgencyScore: 88,
      activity: metadata.activity || 'Mechanical Heavy Lifting & Cargo Handling',
      primaryHazard: 'Dropped Suspended Heavy Load / Rigging Failure',
      precursorCategory: 'Lifting Operations',
      lifeSavingRule: 'Safe Mechanical Lifting',
      failedBarrier: 'Rigging Equipment Integrity & Lift Path Exclusion Barricading',
      barrierStatus: text.includes('snapped') || text.includes('tore') ? 'FAILED' : 'WEAK',
      potentialConsequence: 'Crush fatality from sudden catastrophic dropped heavy load under crane or hoist radius.',
      evidencePhrases: extractPhrases(rawText, ['crane', 'sling', 'rigging', 'suspended load', 'snapped', 'hoist', 'swung', 'drop', 'sharp corner']),
      aiExplanation: 'Lifting operation executed with damaged/unprotected rigging gear or personnel positioned within the uncontrolled dropped-object line of fire.',
    };
  }
  // 5. Hot Work / Welding / Flash Fire
  else if (text.includes('welding') || text.includes('hot work') || text.includes('grinding') || text.includes('torch') || text.includes('spark') || text.includes('flame') || text.includes('flare')) {
    classification = {
      sifPotential: 'HIGH',
      sifPrecursor: 'YES',
      confidence: 92,
      urgencyScore: 89,
      activity: metadata.activity || 'Hot Work & Structural Welding',
      primaryHazard: 'Combustible Gas Leakage / Flash Fire Ignition',
      precursorCategory: 'Hot Work',
      lifeSavingRule: 'Hot Work',
      failedBarrier: 'Continuous LEL Gas Testing & Flameproof Habitat Barrier',
      barrierStatus: 'FAILED',
      potentialConsequence: 'Ignition of volatile hydrocarbon vapor pocket resulting in flash fire or facility conflagration.',
      evidencePhrases: extractPhrases(rawText, ['welding', 'torch', 'hot work', 'gas detector', 'spark', 'flare', 'flame', 'habitat', 'weep']),
      aiExplanation: 'Open flame or thermal ignition source operated in proximity to hydrocarbon lines without active gas testing clearance or fire barrier isolation.',
    };
  }
  // 6. Driving / Journey Management
  else if (text.includes('driving') || text.includes('vehicle') || text.includes('speed') || text.includes('rollover') || text.includes('tanker') || text.includes('seatbelt') || text.includes('crash')) {
    classification = {
      sifPotential: 'HIGH',
      sifPrecursor: 'YES',
      confidence: 90,
      urgencyScore: 82,
      activity: metadata.activity || 'Field Logistics & Heavy Vehicle Transport',
      primaryHazard: 'High-Speed Vehicle Rollover / Loss of Control in Rough Terrain',
      precursorCategory: 'Driving / Journey Management',
      lifeSavingRule: 'Driving & Journey Management',
      failedBarrier: 'Speed Limit Compliance & Mandatory Seatbelt Restraint',
      barrierStatus: 'FAILED',
      potentialConsequence: 'Severe vehicular impact or rollover ejection causing fatal internal trauma.',
      evidencePhrases: extractPhrases(rawText, ['speed', 'tanker', 'road', 'rollover', 'seatbelt', 'slid', 'vehicle', 'blowout']),
      aiExplanation: 'Severe vehicle speed non-compliance or failure to use active occupant restraint while traversing adverse road conditions.',
    };
  }
  // 7. Bypass Safety Controls
  else if (text.includes('bypass') || text.includes('jumper') || text.includes('override') || text.includes('interlock') || text.includes('inhibit') || text.includes('defeat')) {
    classification = {
      sifPotential: 'HIGH',
      sifPrecursor: 'YES',
      confidence: 94,
      urgencyScore: 90,
      activity: metadata.activity || 'Control System & Instrumentation Operations',
      primaryHazard: 'Uncontrolled Process Runaway / Overpressure Catastrophic Trip Defeat',
      precursorCategory: 'Bypass Safety Controls',
      lifeSavingRule: 'Bypassing Safety Controls',
      failedBarrier: 'Management of Change (MOC) & Interlock Override Authorization',
      barrierStatus: 'FAILED',
      potentialConsequence: 'Defeat of automated plant protection trips leading to unmitigated equipment rupture or fire.',
      evidencePhrases: extractPhrases(rawText, ['bypass', 'jumper', 'override', 'interlock', 'without moc', 'bridged', 'disabled']),
      aiExplanation: 'Critical safety instrumented system was bypassed or electrically jumpered without formal engineering authorization or compensating safeguards.',
    };
  }
  // 8. Line of Fire
  else if (text.includes('line of fire') || text.includes('projectile') || text.includes('rotating') || text.includes('entangle') || text.includes('crush') || text.includes('guard')) {
    classification = {
      sifPotential: 'HIGH',
      sifPrecursor: 'YES',
      confidence: 91,
      urgencyScore: 87,
      activity: metadata.activity || 'Machinery Maintenance & Operations',
      primaryHazard: 'Rotating Machinery Entanglement / High Velocity Projectile',
      precursorCategory: 'Line of Fire',
      lifeSavingRule: 'Line of Fire',
      failedBarrier: 'Machine Guarding & Line of Fire Exclusion Zone',
      barrierStatus: 'FAILED',
      potentialConsequence: 'Fatal bodily crushing, limb severance, or projectile impact from energized machinery.',
      evidencePhrases: extractPhrases(rawText, ['line of fire', 'rotating', 'guard', 'entangle', 'ejected', 'projectile', 'unbolted']),
      aiExplanation: 'Worker positioned in the direct physical trajectory of released mechanical energy or unguarded high-speed rotating components.',
    };
  }

  return classification;
}

function extractPhrases(text, keywords) {
  if (!text) return [];
  const sentences = text.split(/[.,;\n]+/);
  const matched = [];
  
  for (const sentence of sentences) {
    const trimmed = sentence.trim();
    if (!trimmed) continue;
    const lower = trimmed.toLowerCase();
    for (const kw of keywords) {
      if (lower.includes(kw) && !matched.includes(trimmed)) {
        matched.push(trimmed);
        break;
      }
    }
  }
  
  return matched.slice(0, 4);
}
