import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { reportService } from '../services/reportService';
import { actionService } from '../services/actionService';

const ReportsContext = createContext(null);

export function ReportsProvider({ children }) {
  const [reports, setReports] = useState([]);
  const [actions, setActions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(Date.now());

  const refreshData = useCallback(async () => {
    try {
      setIsLoading(true);
      const [fetchedReports, fetchedActions] = await Promise.all([
        reportService.getReports(),
        actionService.getActions(),
      ]);
      setReports(fetchedReports);
      setActions(fetchedActions);
    } catch (err) {
      console.error('Failed to load initial data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const updateReportReview = async (reportId, reviewData) => {
    const updated = await reportService.updateReportReview(reportId, reviewData);
    setReports((prev) =>
      prev.map((r) => (r.id === reportId || r.reportId === reportId ? { ...r, ...updated } : r))
    );
    setLastUpdated(Date.now());
    return updated;
  };

  const addReport = async (reportData) => {
    const created = await reportService.createReport(reportData);
    setReports((prev) => [created, ...prev]);
    setLastUpdated(Date.now());
    return created;
  };

  const updateActionStatus = async (actionId, newStatus) => {
    const updated = await actionService.updateActionStatus(actionId, newStatus);
    setActions((prev) =>
      prev.map((a) => (a.actionId === actionId ? { ...a, ...updated } : a))
    );
    setLastUpdated(Date.now());
    return updated;
  };

  const addAction = async (actionData) => {
    const created = await actionService.createAction(actionData);
    setActions((prev) => [created, ...prev]);
    setLastUpdated(Date.now());
    return created;
  };

  return (
    <ReportsContext.Provider
      value={{
        reports,
        actions,
        isLoading,
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
