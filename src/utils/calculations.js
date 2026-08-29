/**
 * Statistical and calculation helpers for SIFT metrics
 */

export function calculateSIFDensity(sifCount, totalCount) {
  if (!totalCount || totalCount === 0) return 0;
  return Number(((sifCount / totalCount) * 100).toFixed(1));
}

export function getRiskLevelFromScore(urgencyScore, sifPotential) {
  if (sifPotential === 'CRITICAL' || urgencyScore >= 90) return 'CRITICAL';
  if (sifPotential === 'HIGH' || urgencyScore >= 75) return 'HIGH';
  if (sifPotential === 'MEDIUM' || urgencyScore >= 50) return 'MEDIUM';
  if (sifPotential === 'LOW' || urgencyScore >= 25) return 'LOW';
  return 'NON-SIF';
}

export function getRiskColorClass(level) {
  switch (level?.toUpperCase()) {
    case 'CRITICAL':
      return {
        bg: 'bg-red-500/10',
        text: 'text-red-700',
        border: 'border-red-200',
        badgeBg: 'bg-red-100 text-red-800 border-red-200',
        indicator: 'bg-red-600',
        hex: '#DC2626'
      };
    case 'HIGH':
      return {
        bg: 'bg-amber-500/10',
        text: 'text-amber-800',
        border: 'border-amber-200',
        badgeBg: 'bg-amber-100 text-amber-900 border-amber-200',
        indicator: 'bg-amber-600',
        hex: '#D97706'
      };
    case 'MEDIUM':
      return {
        bg: 'bg-yellow-500/10',
        text: 'text-yellow-800',
        border: 'border-yellow-200',
        badgeBg: 'bg-yellow-100 text-yellow-900 border-yellow-200',
        indicator: 'bg-yellow-500',
        hex: '#EAB308'
      };
    case 'LOW':
      return {
        bg: 'bg-emerald-500/10',
        text: 'text-emerald-700',
        border: 'border-emerald-200',
        badgeBg: 'bg-emerald-100 text-emerald-800 border-emerald-200',
        indicator: 'bg-emerald-500',
        hex: '#10B981'
      };
    case 'NON-SIF':
    default:
      return {
        bg: 'bg-slate-100',
        text: 'text-slate-700',
        border: 'border-slate-200',
        badgeBg: 'bg-slate-100 text-slate-700 border-slate-200',
        indicator: 'bg-slate-400',
        hex: '#64748B'
      };
  }
}

export function getReviewStatusBadgeClass(status) {
  switch (status?.toUpperCase()) {
    case 'APPROVED':
    case 'VALIDATED':
      return 'bg-emerald-50 text-emerald-800 border-emerald-200';
    case 'PENDING':
      return 'bg-amber-50 text-amber-800 border-amber-200';
    case 'NEEDS CORRECTION':
      return 'bg-red-50 text-red-800 border-red-200';
    case 'MODIFIED':
      return 'bg-sky-50 text-sky-800 border-sky-200';
    default:
      return 'bg-slate-50 text-slate-700 border-slate-200';
  }
}
