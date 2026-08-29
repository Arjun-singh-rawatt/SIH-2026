import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  User,
  Bell,
  Sliders,
  Database,
  Cpu,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useAuth } from '../context/AuthContext';

export function Settings() {
  const { currentUser } = useAuth();
  const [savedSuccess, setSavedSuccess] = useState(false);

  const [criticalAlerts, setCriticalAlerts] = useState(true);
  const [dailyDigest, setDailyDigest] = useState(true);
  const [sifThreshold, setSifThreshold] = useState(85);
  const [defaultTimeRange, setDefaultTimeRange] = useState('30D');

  const handleSave = (e) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 sm:space-y-8 max-w-4xl">
      <PageHeader
        title="Settings & System Preferences"
        subtitle="Manage HSE user profile, alert notifications, AI classification thresholds, and backend endpoints."
      />

      {savedSuccess && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-950 rounded-3xl text-xs font-bold flex items-center gap-2.5 animate-in fade-in shadow-spatial-xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
          <span>System preferences and thresholds updated successfully.</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* User Profile Section */}
        <Card className="border-surface-border/80 rounded-3.5xl shadow-spatial">
          <CardHeader>
            <CardTitle subtitle="Active authenticated user details and organizational assignment">
              User Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 sm:p-6 space-y-4">
            <div className="flex items-center gap-4">
              <img
                src={currentUser?.avatar}
                alt={currentUser?.name}
                className="w-16 h-16 rounded-3xl object-cover border-2 border-emerald-800 shadow-spatial-xs shrink-0"
              />
              <div>
                <h3 className="text-base sm:text-lg font-black text-ink-primary font-sans">{currentUser?.name}</h3>
                <p className="text-xs font-bold text-emerald-800">{currentUser?.title}</p>
                <p className="text-xs text-ink-muted mt-0.5 font-medium">{currentUser?.facilityName}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-3 border-t border-surface-border/60">
              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
                  Email Address
                </label>
                <input
                  type="text"
                  disabled
                  value={currentUser?.email || ''}
                  className="sift-input text-xs bg-[#FAF7F2]"
                />
              </div>

              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
                  Contact Number
                </label>
                <input
                  type="text"
                  disabled
                  value={currentUser?.contactNumber || ''}
                  className="sift-input text-xs bg-[#FAF7F2]"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Model Classification Thresholds */}
        <Card className="border-surface-border/80 rounded-3.5xl shadow-spatial">
          <CardHeader>
            <CardTitle subtitle="Configure sensitivity parameters for automated SIF precursor scoring">
              AI NLP Thresholds & Model Parameters
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 sm:p-6 space-y-4">
            <div>
              <div className="flex justify-between items-center text-xs font-extrabold text-ink-primary mb-1.5">
                <span>SIF Potential Confidence Cutoff</span>
                <span className="font-mono font-black text-emerald-950">{sifThreshold}%</span>
              </div>
              <input
                type="range"
                min={70}
                max={98}
                value={sifThreshold}
                onChange={(e) => setSifThreshold(Number(e.target.value))}
                className="w-full accent-emerald-800 cursor-pointer"
              />
              <p className="text-[11px] text-ink-muted mt-1.5 leading-relaxed">
                Reports with AI confidence below {sifThreshold}% are automatically routed to the Review Queue for human validation.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-3 border-t border-surface-border/60">
              <div>
                <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
                  Default Dashboard Time Horizon
                </label>
                <select
                  value={defaultTimeRange}
                  onChange={(e) => setDefaultTimeRange(e.target.value)}
                  className="sift-select w-full text-xs font-bold py-2 rounded-2xl"
                >
                  <option value="7D">Past 7 Days</option>
                  <option value="30D">Past 30 Days (Recommended)</option>
                  <option value="90D">Past 90 Days</option>
                  <option value="1Y">Past 1 Year</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card className="border-surface-border/80 rounded-3.5xl shadow-spatial">
          <CardHeader>
            <CardTitle subtitle="Manage real-time notifications for critical precursor alerts">
              Notification Preferences
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 sm:p-6 space-y-3">
            <label className="flex items-center justify-between p-3.5 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 cursor-pointer hover:bg-white transition-colors shadow-spatial-xs">
              <div>
                <span className="text-xs font-bold text-ink-primary block">
                  Critical SIF SMS & Push Alerts
                </span>
                <span className="text-[11px] text-ink-muted font-medium">
                  Instant notification when a report with Urgency ≥ 90 is ingested.
                </span>
              </div>
              <input
                type="checkbox"
                checked={criticalAlerts}
                onChange={(e) => setCriticalAlerts(e.target.checked)}
                className="w-4 h-4 rounded text-emerald-800 accent-emerald-800 cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-3.5 rounded-2.5xl bg-[#FAF7F2] border border-surface-border/80 cursor-pointer hover:bg-white transition-colors shadow-spatial-xs">
              <div>
                <span className="text-xs font-bold text-ink-primary block">
                  Daily Executive HSE Digest
                </span>
                <span className="text-[11px] text-ink-muted font-medium">
                  Consolidated daily morning summary of SIF precursor density by site.
                </span>
              </div>
              <input
                type="checkbox"
                checked={dailyDigest}
                onChange={(e) => setDailyDigest(e.target.checked)}
                className="w-4 h-4 rounded text-emerald-800 accent-emerald-800 cursor-pointer"
              />
            </label>
          </CardContent>
        </Card>

        {/* System & Architecture Information */}
        <Card className="border-surface-border/80 rounded-3.5xl bg-[#FAF7F2]/60 shadow-spatial">
          <CardHeader>
            <CardTitle subtitle="Backend connectivity status and persistent vector store schema metadata">
              System Architecture & Vector Metadata
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 sm:p-6 space-y-3 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 font-mono text-[11px]">
              <div className="p-3.5 bg-white rounded-2.5xl border border-surface-border/80 shadow-spatial-xs">
                <span className="text-ink-muted block text-[10px] uppercase font-sans font-extrabold tracking-widest">
                  Vector Engine
                </span>
                <span className="font-bold text-emerald-800">Pinecone Serverless (1536-dim)</span>
              </div>

              <div className="p-3.5 bg-white rounded-2.5xl border border-surface-border/80 shadow-spatial-xs">
                <span className="text-ink-muted block text-[10px] uppercase font-sans font-extrabold tracking-widest">
                  NLP Classifier
                </span>
                <span className="font-bold text-emerald-950">Fine-tuned RoBERTa + DEKRA SIF Engine</span>
              </div>

              <div className="p-3.5 bg-white rounded-2.5xl border border-surface-border/80 shadow-spatial-xs">
                <span className="text-ink-muted block text-[10px] uppercase font-sans font-extrabold tracking-widest">
                  API Gateway
                </span>
                <span className="font-bold text-ink-primary">FastAPI (Python 3.11) Ready</span>
              </div>

              <div className="p-3.5 bg-white rounded-2.5xl border border-surface-border/80 shadow-spatial-xs">
                <span className="text-ink-muted block text-[10px] uppercase font-sans font-extrabold tracking-widest">
                  Standard Alignment
                </span>
                <span className="font-bold text-ink-primary">IOGP Report 459 / 2024</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button type="submit" variant="primary" size="md">
            Save Preferences
          </Button>
        </div>
      </form>
    </div>
  );
}
