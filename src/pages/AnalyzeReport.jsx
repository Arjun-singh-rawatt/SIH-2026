import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Zap,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  Building2,
  Activity,
  FileCheck,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { AIClassificationCard } from '../components/analysis/AIClassificationCard';
import { BarrierAssessment } from '../components/analysis/BarrierAssessment';
import { EvidencePhrase } from '../components/analysis/EvidencePhrase';
import { mockFacilities } from '../data/mockFacilities';
import { analysisService } from '../services/analysisService';
import { useReportsContext } from '../context/ReportsContext';

const PRESET_SCENARIOS = [
  {
    title: 'Digboi 35-Bar Gas Isolation Near Miss',
    facilityId: 'FAC-DIG-02',
    facilityName: 'Digboi Field & Production Complex',
    location: 'Compressor Area, Train-2 Header',
    reportType: 'Near Miss',
    activity: 'Maintenance',
    text: 'During maintenance activity on the compressor manifold, the technician started loosening bolts and removing the discharge valve without proper isolation. The line was still pressurized with 35 bar natural gas. Another technician noticed the pressure gauge needle vibrating and immediately shouted to stop the work before the flange seal blew out.',
  },
  {
    title: 'Moran Confined Separator Entry (42 ppm H2S)',
    facilityId: 'FAC-MOR-03',
    facilityName: 'Moran Oil Field',
    location: 'GGS-4, Separator V-102',
    reportType: 'Unsafe Act',
    activity: 'Vessel Cleaning & Desanding',
    text: 'Two contractor vessel cleaners opened the manway of separator V-102 and entered the confined space to scrape oily sludge without conducting pre-entry atmospheric gas testing and without continuous forced ventilation running. Standby observer was absent from the hatch. Multi-gas detector at the rim later registered 42 ppm H2S and 16.4% oxygen.',
  },
  {
    title: 'Naharkatiya Rig Auxiliary Hoist Wire Snap',
    facilityId: 'FAC-NHK-06',
    facilityName: 'Naharkatiya Deep Drilling Hub',
    location: 'Rig Floor NHK-42, Derrick Substructure',
    reportType: 'Near Miss',
    activity: 'Drilling Operations',
    text: 'While tripping 5-inch drill pipes, the auxiliary air hoist wire rope snapped near the thimble clamp under a 3.2-ton shock load. The suspended drill collar swung erratically through the rotary table area, narrowly missing two roughnecks standing directly in the line of fire before crashing into the drawworks console.',
  },
  {
    title: 'Kumchai Tank Dome Fall Arrest Disconnection (11m)',
    facilityId: 'FAC-KUM-07',
    facilityName: 'Kumchai Oil Field',
    location: 'Crude Storage Tank T-301 Roof',
    reportType: 'Unsafe Act',
    activity: 'Working at Height',
    text: 'Contractor painter was observed scraping rust on the curved roof edge of Crude Tank T-301 at 11 meters height in gusty winds. The worker was wearing a safety harness, but the lanyard was unhooked and dangling freely because no static lifeline had been rigged across the tank dome.',
  },
];

export function AnalyzeReport() {
  const navigate = useNavigate();
  const { addReport } = useReportsContext();

  const [rawText, setRawText] = useState(PRESET_SCENARIOS[0].text);
  const [facilityId, setFacilityId] = useState(PRESET_SCENARIOS[0].facilityId);
  const [location, setLocation] = useState(PRESET_SCENARIOS[0].location);
  const [reportType, setReportType] = useState(PRESET_SCENARIOS[0].reportType);
  const [activity, setActivity] = useState(PRESET_SCENARIOS[0].activity);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStage, setCurrentStage] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [savedReportId, setSavedReportId] = useState(null);

  const handleSelectPreset = (preset) => {
    setRawText(preset.text);
    setFacilityId(preset.facilityId);
    setLocation(preset.location);
    setReportType(preset.reportType);
    setActivity(preset.activity);
    setAnalysisResult(null);
    setSavedReportId(null);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!rawText.trim()) return;

    setIsAnalyzing(true);
    setAnalysisResult(null);
    setSavedReportId(null);

    const selectedFacility = mockFacilities.find((f) => f.facilityId === facilityId) || mockFacilities[0];

    try {
      const result = await analysisService.analyzeReportText(
        rawText,
        {
          facilityId,
          facilityName: selectedFacility.facilityName,
          region: selectedFacility.region,
          location,
          reportType,
          activity,
        },
        (stage) => {
          setCurrentStage(stage);
        }
      );

      const completeReport = {
        ...result,
        facilityId: selectedFacility.facilityId,
        facilityName: selectedFacility.facilityName,
        region: selectedFacility.region,
        location: location || 'Main Processing Section',
        reportType: reportType || 'Near Miss',
        reporterName: 'Interactive AI Analyzer',
        reporterId: 'USR-ANALYZER',
        language: 'English',
        rawReportText: rawText,
      };

      setAnalysisResult(completeReport);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
      setCurrentStage(null);
    }
  };

  const handleSaveToDatabase = async () => {
    if (!analysisResult) return;
    setIsSaving(true);
    try {
      const created = await addReport(analysisResult);
      setSavedReportId(created.reportId);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader
        title="Live AI Safety Report Analyzer"
        subtitle="Simulate NLP feature extraction, Life-Saving Rule mapping, barrier failure diagnosis, and SIF precursor scoring."
      />

      {/* Preset Quick Loader Strip */}
      <div className="bg-white border border-surface-border/80 rounded-3.5xl p-5 sm:p-6 shadow-spatial">
        <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block mb-3">
          Load Sample Field Observation Scenario
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {PRESET_SCENARIOS.map((preset) => (
            <button
              key={preset.title}
              type="button"
              onClick={() => handleSelectPreset(preset)}
              className="p-3.5 rounded-2.5xl border border-surface-border/80 bg-[#FAF7F2] hover:bg-white hover:border-amber-300/80 hover:shadow-spatial-xs transition-all text-left cursor-pointer group"
            >
              <div className="flex items-center gap-1.5 text-xs font-bold text-ink-primary group-hover:text-amber-950">
                <Zap className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                <span className="truncate">{preset.title}</span>
              </div>
              <span className="text-[10px] text-ink-muted block mt-1 truncate font-medium">
                {preset.facilityName}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Sandbox Form */}
      <form onSubmit={handleAnalyze} className="space-y-4">
        <Card className="p-6 sm:p-7 border-surface-border/80 rounded-3.5xl shadow-spatial">
          <div className="space-y-5">
            {/* Free-text Observation Textarea */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-extrabold uppercase tracking-wider text-ink-primary flex items-center gap-2">
                  <FileCheck className="w-4 h-4 text-emerald-800" />
                  <span>Safety Observation / Incident Free-Text Narrative</span>
                </label>
                <span className="text-[11px] text-ink-muted font-mono font-medium">{rawText.length} characters</span>
              </div>
              <textarea
                rows={5}
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="Paste or type raw safety report narrative (e.g. valve unbolting, H2S sensor alarm, crane sling pinch, working at height without lanyard)..."
                className="sift-input text-xs sm:text-sm font-sans leading-relaxed resize-y min-h-[120px]"
                required
              />
            </div>

            {/* Optional Metadata Controls */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 pt-3 border-t border-surface-border/60">
              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
                  OIL Facility
                </label>
                <select
                  value={facilityId}
                  onChange={(e) => setFacilityId(e.target.value)}
                  className="sift-select w-full text-xs font-bold py-2 px-3 rounded-2xl"
                >
                  {mockFacilities.map((f) => (
                    <option key={f.facilityId} value={f.facilityId}>
                      {f.shortName}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
                  Location / Skid
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Header Manifold #3"
                  className="sift-input text-xs py-2 px-3 rounded-2xl"
                />
              </div>

              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
                  Report Type
                </label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="sift-select w-full text-xs font-bold py-2 px-3 rounded-2xl"
                >
                  <option value="Near Miss">Near Miss</option>
                  <option value="Unsafe Act">Unsafe Act</option>
                  <option value="Unsafe Condition">Unsafe Condition</option>
                  <option value="Incident">Incident</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
                  Operational Activity
                </label>
                <input
                  type="text"
                  value={activity}
                  onChange={(e) => setActivity(e.target.value)}
                  placeholder="e.g. Maintenance, Rig Tripping"
                  className="sift-input text-xs py-2 px-3 rounded-2xl"
                />
              </div>
            </div>

            {/* Trigger Button */}
            <div className="pt-3 flex items-center justify-between">
              <span className="text-[11px] text-ink-muted hidden sm:inline font-medium">
                Simulates NLP entity extraction, Life-Saving Rule matching, and SIF potential scoring.
              </span>
              <Button
                type="submit"
                variant="amber"
                size="md"
                isLoading={isAnalyzing}
                icon={Sparkles}
                className="w-full sm:w-auto font-black shadow-btn-amber"
              >
                Analyze Safety Report
              </Button>
            </div>
          </div>
        </Card>
      </form>

      {/* Simulated Multi-Stage Loading Indicator */}
      {isAnalyzing && (
        <div className="p-8 sm:p-10 rounded-3.5xl bg-white border border-emerald-200/80 shadow-spatial-lg text-center space-y-4 animate-in fade-in">
          <div className="relative w-14 h-14 mx-auto">
            <div className="absolute inset-0 rounded-full border-4 border-surface-border" />
            <div className="absolute inset-0 rounded-full border-4 border-emerald-800 border-t-transparent animate-spin" />
            <Sparkles className="w-6 h-6 text-emerald-800 absolute inset-0 m-auto" />
          </div>
          <div>
            <h4 className="text-sm sm:text-base font-extrabold text-ink-primary">
              {currentStage?.name || 'Processing NLP model inference...'}
            </h4>
            <p className="text-xs text-ink-muted mt-1 font-mono">
              Step {currentStage?.step || 1} of 5 · SIFT Precursor Engine v2.4
            </p>
          </div>
        </div>
      )}

      {/* Real-Time Assessment Results */}
      {analysisResult && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-emerald-50 border border-emerald-200/90 rounded-3.5xl p-5 text-xs font-bold text-emerald-950 shadow-spatial-xs">
            <div className="flex items-center gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0" />
              <span>AI Analysis Complete: SIF potential and precursor entities extracted successfully.</span>
            </div>

            {!savedReportId ? (
              <Button
                variant="primary"
                size="sm"
                onClick={handleSaveToDatabase}
                isLoading={isSaving}
              >
                Save & Add to Reports Database
              </Button>
            ) : (
              <Button
                variant="secondary"
                size="sm"
                iconRight={ArrowRight}
                onClick={() => navigate(`/reports/${savedReportId}`)}
              >
                View Saved Report #{savedReportId}
              </Button>
            )}
          </div>

          {/* Result Card Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-7">
            <div className="lg:col-span-6 space-y-6">
              <Card className="border-surface-border/80 rounded-3.5xl shadow-spatial">
                <CardHeader>
                  <CardTitle subtitle="Highlighted extracted evidence triggers that informed the AI model">
                    Evidence Extraction Highlight
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-5 sm:p-6">
                  <EvidencePhrase
                    rawText={analysisResult.rawReportText}
                    evidencePhrases={analysisResult.evidencePhrases}
                  />
                </CardContent>
              </Card>

              <BarrierAssessment report={analysisResult} />
            </div>

            <div className="lg:col-span-6 space-y-6">
              <AIClassificationCard report={analysisResult} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
