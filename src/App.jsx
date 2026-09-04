import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ReportsProvider } from './context/ReportsContext';
import { AppShell } from './components/layout/AppShell';

import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Reports } from './pages/Reports';
import { ReportDetails } from './pages/ReportDetails';
import { AnalyzeReport } from './pages/AnalyzeReport';
import { Intelligence } from './pages/Intelligence';
import { LifeSavingRules } from './pages/LifeSavingRules';
import { LifeSavingRuleDetails } from './pages/LifeSavingRuleDetails';
import { ReviewQueue } from './pages/ReviewQueue';
import { Actions } from './pages/Actions';
import { Facilities } from './pages/Facilities';
import { FacilityDetails } from './pages/FacilityDetails';
import { Settings } from './pages/Settings';
import { ReportSafetyConcern } from './pages/ReportSafetyConcern';
import { MyReports } from './pages/MyReports';
import { FieldLifeSavingRules } from './pages/FieldLifeSavingRules';

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ReportsProvider>
          <Routes>
            {/* Public Landing Route */}
            <Route path="/" element={<Login />} />
            <Route path="/login" element={<Login />} />

            {/* Authenticated Layout Shell */}
            <Route element={<AppShell />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/report" element={<ReportSafetyConcern />} />
              <Route path="/my-reports" element={<MyReports />} />
              <Route path="/field-life-saving-rules" element={<FieldLifeSavingRules />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/reports/:id" element={<ReportDetails />} />
              <Route path="/analyze" element={<AnalyzeReport />} />
              <Route path="/intelligence" element={<Intelligence />} />
              <Route path="/life-saving-rules" element={<LifeSavingRules />} />
              <Route path="/life-saving-rules/:id" element={<LifeSavingRuleDetails />} />
              <Route path="/review" element={<ReviewQueue />} />
              <Route path="/actions" element={<Actions />} />
              <Route path="/facilities" element={<Facilities />} />
              <Route path="/facilities/:id" element={<FacilityDetails />} />
              <Route path="/settings" element={<Settings />} />
            </Route>

            {/* Catch-all fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ReportsProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
