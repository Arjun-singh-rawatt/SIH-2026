import { mockReports } from '../data/mockReports';
import { mockFacilities } from '../data/mockFacilities';
import { mockLifeSavingRules } from '../data/mockLifeSavingRules';
import { mockActions } from '../data/mockActions';

export const analyticsService = {
  /**
   * Executive KPI cards data
   */
  async getDashboardMetrics(timeRange = '30D') {
    await new Promise((resolve) => setTimeout(resolve, 30));

    // Dynamic metrics aligned with enterprise numbers
    return {
      totalReports: {
        value: 12482,
        formatted: '12,482',
        change: '+8.4%',
        changeType: 'neutral', // volume increase
        subtitle: 'vs previous 30-day period',
      },
      sifPotential: {
        value: 2341,
        formatted: '2,341',
        percentage: '18.7%',
        change: '+2.1%',
        changeType: 'increase', // risk increase is warning
        subtitle: '18.7% of total reports flagged',
      },
      highUrgency: {
        value: 684,
        formatted: '684',
        percentage: '29.2%',
        change: '-4.6%',
        changeType: 'decrease',
        subtitle: '29.2% of SIF reports (Urgency ≥ 80)',
      },
      openActions: {
        value: 126,
        formatted: '126',
        overdueCount: 18,
        change: '18 Overdue',
        changeType: 'warning',
        subtitle: '34 in progress, 18 require escalation',
      },
    };
  },

  /**
   * SIF Exposure Trend by Time Range (7D, 30D, 90D, 1Y)
   */
  async getTrendData(timeRange = '30D') {
    await new Promise((resolve) => setTimeout(resolve, 30));

    if (timeRange === '7D') {
      return [
        { label: 'Day 1', date: '22 Aug', total: 42, sifPotential: 8, critical: 2, nonSif: 34 },
        { label: 'Day 2', date: '23 Aug', total: 48, sifPotential: 11, critical: 3, nonSif: 37 },
        { label: 'Day 3', date: '24 Aug', total: 39, sifPotential: 7, critical: 1, nonSif: 32 },
        { label: 'Day 4', date: '25 Aug', total: 55, sifPotential: 14, critical: 4, nonSif: 41 },
        { label: 'Day 5', date: '26 Aug', total: 51, sifPotential: 12, critical: 3, nonSif: 39 },
        { label: 'Day 6', date: '27 Aug', total: 60, sifPotential: 16, critical: 5, nonSif: 44 },
        { label: 'Day 7', date: '28 Aug', total: 58, sifPotential: 15, critical: 4, nonSif: 43 },
      ];
    }

    if (timeRange === '90D') {
      return [
        { label: 'Jun W1', total: 240, sifPotential: 44, critical: 12, nonSif: 196 },
        { label: 'Jun W2', total: 260, sifPotential: 49, critical: 14, nonSif: 211 },
        { label: 'Jun W3', total: 230, sifPotential: 38, critical: 9, nonSif: 192 },
        { label: 'Jun W4', total: 275, sifPotential: 52, critical: 15, nonSif: 223 },
        { label: 'Jul W1', total: 290, sifPotential: 58, critical: 17, nonSif: 232 },
        { label: 'Jul W2', total: 310, sifPotential: 62, critical: 19, nonSif: 248 },
        { label: 'Jul W3', total: 280, sifPotential: 51, critical: 13, nonSif: 229 },
        { label: 'Jul W4', total: 320, sifPotential: 65, critical: 20, nonSif: 255 },
        { label: 'Aug W1', total: 335, sifPotential: 71, critical: 22, nonSif: 264 },
        { label: 'Aug W2', total: 310, sifPotential: 60, critical: 18, nonSif: 250 },
        { label: 'Aug W3', total: 345, sifPotential: 74, critical: 24, nonSif: 271 },
        { label: 'Aug W4', total: 360, sifPotential: 78, critical: 25, nonSif: 282 },
      ];
    }

    if (timeRange === '1Y') {
      return [
        { label: 'Sep 25', total: 980, sifPotential: 165, critical: 42, nonSif: 815 },
        { label: 'Oct 25', total: 1020, sifPotential: 182, critical: 49, nonSif: 838 },
        { label: 'Nov 25', total: 950, sifPotential: 160, critical: 38, nonSif: 790 },
        { label: 'Dec 25', total: 1100, sifPotential: 215, critical: 61, nonSif: 885 },
        { label: 'Jan 26', total: 1040, sifPotential: 195, critical: 54, nonSif: 845 },
        { label: 'Feb 26', total: 990, sifPotential: 178, critical: 48, nonSif: 812 },
        { label: 'Mar 26', total: 1150, sifPotential: 228, critical: 67, nonSif: 922 },
        { label: 'Apr 26', total: 1080, sifPotential: 204, critical: 59, nonSif: 876 },
        { label: 'May 26', total: 1120, sifPotential: 218, critical: 63, nonSif: 902 },
        { label: 'Jun 26', total: 1190, sifPotential: 235, critical: 72, nonSif: 955 },
        { label: 'Jul 26', total: 1240, sifPotential: 246, critical: 76, nonSif: 994 },
        { label: 'Aug 26', total: 1280, sifPotential: 265, critical: 84, nonSif: 1015 },
      ];
    }

    // Default 30D
    return [
      { label: 'Aug 01', total: 41, sifPotential: 7, critical: 2, nonSif: 34 },
      { label: 'Aug 04', total: 46, sifPotential: 9, critical: 3, nonSif: 37 },
      { label: 'Aug 07', total: 52, sifPotential: 11, critical: 3, nonSif: 41 },
      { label: 'Aug 10', total: 38, sifPotential: 6, critical: 1, nonSif: 32 },
      { label: 'Aug 13', total: 49, sifPotential: 10, critical: 2, nonSif: 39 },
      { label: 'Aug 16', total: 57, sifPotential: 13, critical: 4, nonSif: 44 },
      { label: 'Aug 19', total: 53, sifPotential: 12, critical: 4, nonSif: 41 },
      { label: 'Aug 22', total: 61, sifPotential: 15, critical: 5, nonSif: 46 },
      { label: 'Aug 25', total: 64, sifPotential: 17, critical: 6, nonSif: 47 },
      { label: 'Aug 28', total: 68, sifPotential: 18, critical: 6, nonSif: 50 },
    ];
  },

  /**
   * SIF Precursors by Category (Bar Chart)
   */
  async getPrecursorBreakdown() {
    await new Promise((resolve) => setTimeout(resolve, 20));
    return [
      { category: 'Energy Isolation', count: 624, critical: 218, density: 34.9, color: '#D97706' },
      { category: 'Line of Fire', count: 785, critical: 242, density: 30.8, color: '#EA580C' },
      { category: 'Confined Space', count: 412, critical: 168, density: 40.8, color: '#DC2626' },
      { category: 'Hot Work', count: 512, critical: 145, density: 28.3, color: '#F59E0B' },
      { category: 'Working at Height', count: 498, critical: 124, density: 24.9, color: '#0284C7' },
      { category: 'Lifting Operations', count: 430, critical: 118, density: 27.4, color: '#7C3AED' },
      { category: 'Bypass Controls', count: 284, critical: 102, density: 35.9, color: '#B91C1C' },
      { category: 'Driving / Journey', count: 360, critical: 58, density: 16.1, color: '#059669' },
    ];
  },

  /**
   * Ranking facilities based on SIF precursor density
   */
  async getFacilityRiskRanking() {
    await new Promise((resolve) => setTimeout(resolve, 25));
    return [...mockFacilities].sort((a, b) => b.sifDensity - a.sifDensity);
  },

  /**
   * High-Risk Activities Breakdown
   */
  async getActivityRiskBreakdown() {
    await new Promise((resolve) => setTimeout(resolve, 20));
    return [
      { activity: 'Plant & Equipment Maintenance', totalReports: 1840, sifCount: 482, density: 26.2, risk: 'CRITICAL' },
      { activity: 'Wellhead & Drilling Operations', totalReports: 1420, sifCount: 396, density: 27.9, risk: 'CRITICAL' },
      { activity: 'Flange Breaking & Piping Tie-in', totalReports: 890, sifCount: 268, density: 30.1, risk: 'CRITICAL' },
      { activity: 'Heavy Crane Cargo Hoisting', totalReports: 760, sifCount: 198, density: 26.0, risk: 'HIGH' },
      { activity: 'Vessel Cleaning & Desanding', totalReports: 510, sifCount: 184, density: 36.1, risk: 'CRITICAL' },
      { activity: 'Structural Welding & Grinding', totalReports: 940, sifCount: 220, density: 23.4, risk: 'HIGH' },
      { activity: 'Remote Road Haulage & Driving', totalReports: 1120, sifCount: 162, density: 14.5, risk: 'MEDIUM' },
    ];
  },

  /**
   * Top recurring failed barriers
   */
  async getBarrierFailureStats() {
    await new Promise((resolve) => setTimeout(resolve, 20));
    return [
      { barrier: 'Zero Energy Isolation Verification', failures: 342, severity: 'CRITICAL', percentage: 28.5 },
      { barrier: 'Exclusion Barricades & Line of Fire', failures: 298, severity: 'CRITICAL', percentage: 24.8 },
      { barrier: 'Multi-Gas Atmospheric Pre-testing', failures: 186, severity: 'CRITICAL', percentage: 15.5 },
      { barrier: '100% Fall Arrest Harness Anchor', failures: 164, severity: 'HIGH', percentage: 13.7 },
      { barrier: 'Rigging Sling Inspection & Corner Pads', failures: 122, severity: 'HIGH', percentage: 10.2 },
      { barrier: 'MOC Safety Interlock Bypass Sign-off', failures: 88, severity: 'HIGH', percentage: 7.3 },
    ];
  },

  /**
   * Priority Attention actionable findings panel
   */
  async getPriorityAlerts() {
    await new Promise((resolve) => setTimeout(resolve, 20));
    return [
      {
        id: 'ALT-01',
        level: 'CRITICAL',
        title: 'Energy Isolation Breakdown at Digboi Complex',
        subtitle: '14 SIF precursors detected during manifold valve servicing in the last 14 days.',
        facilityId: 'FAC-DIG-02',
        facilityName: 'Digboi Field & Production Complex',
        precursor: 'Energy Isolation',
        failedBarrier: 'Zero Energy Verification & Bleed Port Clearance',
        reportCount: 14,
        actionUrl: '/reports?facilityId=FAC-DIG-02&sifPotential=HIGH',
      },
      {
        id: 'ALT-02',
        level: 'CRITICAL',
        title: '3 High-Urgency Confined Space Reports Pending Review',
        subtitle: 'Unventilated separator vessel entries with H2S readings >40 ppm awaiting HSE sign-off.',
        facilityId: 'FAC-MOR-03',
        facilityName: 'Moran Oil Field',
        precursor: 'Confined Space',
        failedBarrier: 'Atmospheric Gas Testing & Standby Watchman',
        reportCount: 3,
        actionUrl: '/review?filter=CRITICAL_HIGH',
      },
      {
        id: 'ALT-03',
        level: 'HIGH',
        title: 'Naharkatiya Rig Floor Line of Fire & Rigging Degradation',
        subtitle: 'Recurrent auxiliary hoist wire rope and sling pinch incidents under shock loads.',
        facilityId: 'FAC-NHK-06',
        facilityName: 'Naharkatiya Deep Drilling Hub',
        precursor: 'Lifting Operations',
        failedBarrier: 'Rigging Sling Edge Protection & Exclusion Line',
        reportCount: 8,
        actionUrl: '/reports?facilityId=FAC-NHK-06&precursorCategory=Lifting+Operations',
      },
      {
        id: 'ALT-04',
        level: 'HIGH',
        title: 'Barekuri Gas Gathering Compressor Trip Jumpers',
        subtitle: 'Safety temperature and vibration interlocks bridged to bypass nuisance morning cold-start trips.',
        facilityId: 'FAC-BAR-10',
        facilityName: 'Barekuri Gas Gathering Station',
        precursor: 'Bypass Safety Controls',
        failedBarrier: 'MOC Override Authorization',
        reportCount: 4,
        actionUrl: '/reports?facilityId=FAC-BAR-10',
      },
    ];
  },
};
