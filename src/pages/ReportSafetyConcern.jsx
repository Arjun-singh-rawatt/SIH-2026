import React, { useRef, useState } from 'react';
import {
  Camera,
  CheckCircle2,
  FileText,
  LocateFixed,
  MapPin,
  Mic,
  MicOff,
  Send,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useReportsContext } from '../context/ReportsContext';
import { mockFacilities } from '../data/mockFacilities';
import { FieldShell } from '../components/layout/FieldShell';

const initialLocation = {
  name: 'Current field location',
  latitude: 27.3582,
  longitude: 95.3184,
};

export function ReportSafetyConcern() {
  const { currentUser } = useAuth();
  const { addReport } = useReportsContext();
  const photoInputRef = useRef(null);
  const recorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState(initialLocation);
  const [photoName, setPhotoName] = useState('');
  const [voiceName, setVoiceName] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLocating, setIsLocating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitState, setSubmitState] = useState(null);

  const facility = mockFacilities.find((item) => item.facilityId === currentUser?.facilityId) || mockFacilities[0];

  const handleLocation = () => {
    if (!navigator.geolocation) return;
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          name: 'Current field location',
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
        setIsLocating(false);
      },
      () => setIsLocating(false),
      { enableHighAccuracy: true, timeout: 8000 }
    );
  };

  const handleVoice = async () => {
    if (isRecording) {
      recorderRef.current?.stop();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      recordedChunksRef.current = [];
      recorder.ondataavailable = (event) => recordedChunksRef.current.push(event.data);
      recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
        if (recordedChunksRef.current.length) setVoiceName('Voice observation recorded');
        setIsRecording(false);
      };
      recorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Microphone access was not available:', error);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!description.trim()) return;

    setIsSubmitting(true);
    setSubmitState(null);
    try {
      const created = await addReport({
        reporterId: currentUser?.userId,
        facilityId: facility.facilityId,
        location: `${location.name} (${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)})`,
        rawReportText: description.trim(),
        reportType: 'Unsafe Condition',
        activity: 'Field Safety Observation',
        potentialConsequence: 'Requires safety review and mitigation',
      });
      setSubmitState({ type: 'success', reportId: created.reportId });
      setDescription('');
    } catch (error) {
      console.error('Unable to submit report:', error);
      setSubmitState({ type: 'error' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <FieldShell activePage="/report">
        <main className="mx-auto w-full max-w-[1040px] px-5 py-6 sm:px-8 lg:py-7">
          <div className="mb-5">
            <div className="mb-2 flex items-center justify-end gap-3 text-[10px] font-bold uppercase tracking-[0.26em] text-[#73757a]">
              <span className="h-0.5 w-6 bg-[#0a705a]" /> Safer operations. Stronger tomorrow.
            </div>
            <h1 className="text-[2.15rem] font-black leading-tight tracking-[-0.04em] sm:text-[2.5rem]">Report a Safety Concern</h1>
            <p className="mt-1.5 text-sm text-[#595d65] sm:text-base">Log critical safety observations immediately to ensure prompt action and mitigation.</p>
          </div>

          <form onSubmit={handleSubmit} className="rounded-2xl border border-[#eadabb] bg-white/95 p-5 shadow-[0_14px_34px_rgba(61,53,41,0.07)] sm:p-6">
            <div className="flex flex-col gap-4 border-b border-[#e5e1d9] pb-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3 text-xs font-extrabold uppercase tracking-[0.08em]">
                <FileText className="h-5 w-5 text-[#00654f]" /> TELL US WHAT HAPPENED
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={handleVoice} className={`inline-flex items-center gap-2 rounded-md border px-3 py-2 text-xs font-bold ${isRecording ? 'border-red-300 bg-red-50 text-red-700' : 'border-[#bfd9d1] bg-[#f3faf7] text-[#075b4b]'}`}>
                  {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  {isRecording ? 'Stop Recording' : 'Record Voice'}
                </button>
                <button type="button" onClick={() => photoInputRef.current?.click()} className="inline-flex items-center gap-2 rounded-md border border-[#bfd9d1] bg-[#f3faf7] px-3 py-2 text-xs font-bold text-[#075b4b]">
                  <Camera className="h-4 w-4" /> Add Photo
                </button>
                <input ref={photoInputRef} type="file" accept="image/*" className="hidden" onChange={(event) => setPhotoName(event.target.files?.[0]?.name || '')} />
              </div>
            </div>

            <textarea value={description} onChange={(event) => setDescription(event.target.value)} maxLength={1000} required placeholder="Describe the concern in detail..." className="mt-4 min-h-[126px] w-full resize-none rounded-md border border-[#dce1e5] bg-[#fbfcfd] px-4 py-3 text-sm text-[#202833] outline-none transition focus:border-[#047857] focus:ring-2 focus:ring-[#047857]/15" />
            <div className="mt-1 flex justify-between text-[11px] text-[#77808d]">
              <span>{photoName || voiceName || 'Attachments remain with this field submission.'}</span>
              <span>{description.length}/1000</span>
            </div>

            <div className="mt-4 border-t border-[#e5e1d9] pt-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3 text-xs font-extrabold uppercase tracking-[0.08em]">
                  <MapPin className="h-5 w-5 text-[#00705a]" /> Location (Auto-detected)
                </div>
                <button type="button" onClick={handleLocation} disabled={isLocating} className="inline-flex items-center gap-2 self-start rounded-md border border-[#bfd9d1] bg-[#f3faf7] px-3 py-2 text-xs font-bold text-[#075b4b] disabled:opacity-60 sm:self-auto">
                  <LocateFixed className="h-4 w-4" /> {isLocating ? 'Locating...' : 'Use Current Location'}
                </button>
              </div>
              <div
                className="mt-3 h-[132px] rounded-lg border border-[#d5d1c8] bg-[#fafbf9]"
                aria-label={`Location preview for ${facility.shortName}`}
              />
            </div>

            <div className="mt-4 border-t border-[#e5e1d9] pt-4">
              <button type="submit" disabled={isSubmitting || !description.trim()} className="flex w-full items-center justify-center gap-3 rounded-lg bg-gradient-to-r from-[#00745d] to-[#00634f] py-3 text-sm font-extrabold tracking-[0.04em] text-white shadow-btn-emerald transition hover:from-[#058867] disabled:cursor-not-allowed disabled:opacity-50">
                <Send className="h-5 w-5" /> {isSubmitting ? 'SUBMITTING...' : 'SUBMIT REPORT'}
              </button>
              {submitState?.type === 'success' && <p className="mt-2 flex items-center justify-center gap-2 text-xs font-semibold text-[#00705a]"><CheckCircle2 className="h-4 w-4" /> Report submitted. Tracking ID: {submitState.reportId}</p>}
              {submitState?.type === 'error' && <p className="mt-2 text-center text-xs font-semibold text-red-700">We could not submit the report. Please try again.</p>}
            </div>
          </form>
        </main>
    </FieldShell>
  );
}
