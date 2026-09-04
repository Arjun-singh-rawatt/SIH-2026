import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { reportService } from '../services/reportService';
import { actionService } from '../services/actionService';
import { analyticsService } from '../services/analyticsService';
import { demoReports } from '../data/demoReports';

const ReportsContext = createContext(null);

export function ReportsProvider({ children }) {
  const [reports, setReports] = useState([]);
  const [actions, setActions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(Date.now());

  const refreshData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const [fetchedReports, fetchedActions] = await Promise.all([
        reportService.getReports({}, 1, 100),
        actionService.getActions({}, 1, 100),
      ]);
      const fetchedReportIds = new Set(fetchedReports.map((report) => report.reportId));
      const reportsWithDemoData = [
        ...demoReports.filter((report) => !fetchedReportIds.has(report.reportId)),
        ...fetchedReports,
      ];
      setReports(reportsWithDemoData);
      setActions(fetchedActions);
      analyticsService.invalidateCache();
    } catch (err) {
      console.error('Failed to load safety reports from backend:', err);
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const updateReportReview = async (reportId, reviewData) => {
    try {
      const updated = await reportService.updateReportReview(reportId, reviewData);
      setReports((prev) =>
        prev.map((r) => (r.id === reportId || r.reportId === reportId ? { ...r, ...updated } : r))
      );
      analyticsService.invalidateCache();
      setLastUpdated(Date.now());
      return updated;
    } catch (err) {
      console.error('Failed to update report review:', err);
      throw err;
    }
  };

  const addReport = async (reportData) => {
    try {
      const created = await reportService.createReport(reportData);
      setReports((prev) => [created, ...prev]);
      analyticsService.invalidateCache();
      setLastUpdated(Date.now());
      return created;
    } catch (err) {
      console.error('Failed to create report:', err);
      throw err;
    }
  };

  const updateActionStatus = async (actionId, newStatus) => {
    try {
      const updated = await actionService.updateActionStatus(actionId, newStatus);
      setActions((prev) =>
        prev.map((a) => (a.actionId === actionId || a.id === actionId ? { ...a, ...updated } : a))
      );
      analyticsService.invalidateCache();
      setLastUpdated(Date.now());
      return updated;
    } catch (err) {
      console.error('Failed to update action status:', err);
      throw err;
    }
  };

  const addAction = async (actionData) => {
    try {
      const created = await actionService.createAction(actionData);
      setActions((prev) => [created, ...prev]);
      analyticsService.invalidateCache();
      setLastUpdated(Date.now());
      return created;
    } catch (err) {
      console.error('Failed to create action item:', err);
      throw err;
    }
  };

  return (
    <ReportsContext.Provider
      value={{
        reports,
        actions,
        isLoading,
        error,
        lastUpdated,
        refreshData,
        updateReportReview,
        addReport,
        updateActionStatus,
        addAction,
      }}
    >
      {children}
    </ReportsContext.Provider>
  );
}

export function useReportsContext() {
  const context = useContext(ReportsContext);
  if (!context) {
    throw new Error('useReportsContext must be used within a ReportsProvider');
  }
  return context;
}
