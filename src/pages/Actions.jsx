import React, { useState, useMemo } from 'react';
import {
  ListTodo,
  Plus,
  Filter,
  CheckCircle2,
  Clock,
  AlertTriangle,
  RotateCcw,
  Search,
} from 'lucide-react';
import { PageHeader } from '../components/layout/PageHeader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Tabs } from '../components/ui/Tabs';
import { Button } from '../components/ui/Button';
import { ActionTable } from '../components/actions/ActionTable';
import { CreateActionModal } from '../components/actions/CreateActionModal';
import { mockFacilities } from '../data/mockFacilities';
import { useReportsContext } from '../context/ReportsContext';

export function Actions() {
  const { actions, updateActionStatus, addAction } = useReportsContext();

  const [activeTab, setActiveTab] = useState('ALL');
  const [search, setSearch] = useState('');
  const [facilityFilter, setFacilityFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const stats = useMemo(() => {
    const total = actions.length;
    const open = actions.filter((a) => a.status === 'Open').length;
    const inProgress = actions.filter((a) => a.status === 'In Progress').length;
    const completed = actions.filter((a) => a.status === 'Completed').length;
    const overdue = actions.filter((a) => a.status === 'Overdue').length;
    return { total, open, inProgress, completed, overdue };
  }, [actions]);

  const tabs = [
    { id: 'ALL', label: 'All Actions', count: stats.total },
    { id: 'Open', label: 'Open', count: stats.open },
    { id: 'In Progress', label: 'In Progress', count: stats.inProgress },
    { id: 'Overdue', label: 'Overdue', count: stats.overdue },
    { id: 'Completed', label: 'Completed', count: stats.completed },
  ];

  const filteredActions = useMemo(() => {
    return actions.filter((act) => {
      if (activeTab !== 'ALL' && act.status !== activeTab) return false;
      if (facilityFilter !== 'ALL' && act.facilityId !== facilityFilter) return false;
      if (priorityFilter !== 'ALL' && act.priority !== priorityFilter) return false;
      if (search.trim()) {
        const q = search.toLowerCase();
        const matches =
          act.actionId.toLowerCase().includes(q) ||
          act.reportId.toLowerCase().includes(q) ||
          act.description.toLowerCase().includes(q) ||
          act.assigneeName.toLowerCase().includes(q) ||
          act.facilityName.toLowerCase().includes(q);
        if (!matches) return false;
      }
      return true;
    });
  }, [actions, activeTab, facilityFilter, priorityFilter, search]);

  const handleResetFilters = () => {
    setActiveTab('ALL');
    setSearch('');
    setFacilityFilter('ALL');
    setPriorityFilter('ALL');
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader
        title="Corrective & Preventative Actions (CAPA)"
        subtitle="Track, assign, and enforce engineering and administrative barrier remediations."
        actions={
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => setIsCreateModalOpen(true)}
          >
            Create New Action
          </Button>
        }
      />

      {/* KPI Stats Counter Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3.5 sm:gap-4">
        <Card className="p-4 sm:p-5 bg-white rounded-3xl">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-ink-muted block">
            Total CAPA Items
          </span>
          <span className="text-2xl sm:text-3xl font-black text-ink-primary font-mono mt-1 block">
            {stats.total}
          </span>
        </Card>

        <Card className="p-4 sm:p-5 bg-amber-50/40 border-amber-200/80 rounded-3xl">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-amber-950 block">
            Open / Pending
          </span>
          <span className="text-2xl sm:text-3xl font-black text-amber-950 font-mono mt-1 block">
            {stats.open}
          </span>
        </Card>

        <Card className="p-4 sm:p-5 bg-sky-50/40 border-sky-200/80 rounded-3xl">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-sky-950 block">
            In Progress
          </span>
          <span className="text-2xl sm:text-3xl font-black text-sky-950 font-mono mt-1 block">
            {stats.inProgress}
          </span>
        </Card>

        <Card className="p-4 sm:p-5 bg-red-50/40 border-red-200/80 rounded-3xl">
          <span className="text-[10px] font-black uppercase tracking-widest text-red-950 block">
            Overdue Escalations
          </span>
          <span className="text-2xl sm:text-3xl font-black text-red-950 font-mono mt-1 block">
            {stats.overdue}
          </span>
        </Card>

        <Card className="p-4 sm:p-5 bg-emerald-50/40 border-emerald-200/80 rounded-3xl">
          <span className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-950 block">
            Completed & Verified
          </span>
          <span className="text-2xl sm:text-3xl font-black text-emerald-950 font-mono mt-1 block">
            {stats.completed}
          </span>
        </Card>
      </div>

      {/* Filters & Tabs */}
      <div className="bg-white border border-surface-border/80 rounded-3.5xl p-5 sm:p-6 shadow-spatial space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

          <div className="relative w-full lg:max-w-xs">
            <Search className="w-4 h-4 text-ink-muted absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search action ID, owner, or description..."
              className="sift-input pl-10 text-xs py-2 rounded-full"
            />
          </div>
        </div>

        {/* Secondary Filter Dropdowns */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 pt-3 border-t border-surface-border/60">
          <div>
            <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
              Filter by Facility
            </label>
            <select
              value={facilityFilter}
              onChange={(e) => setFacilityFilter(e.target.value)}
              className="sift-select w-full text-xs font-medium py-2 px-3 rounded-2xl"
            >
              <option value="ALL">All Operational Facilities</option>
              {mockFacilities.map((f) => (
                <option key={f.facilityId} value={f.facilityId}>
                  {f.shortName}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-extrabold uppercase tracking-widest text-ink-muted mb-1">
              Filter by Priority
            </label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="sift-select w-full text-xs font-bold py-2 px-3 rounded-2xl"
            >
              <option value="ALL">All Priorities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div className="flex items-end justify-end">
            {(facilityFilter !== 'ALL' || priorityFilter !== 'ALL' || search) && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleResetFilters}
                icon={RotateCcw}
                className="text-xs"
              >
                Reset Filters
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Action Items Table */}
      <ActionTable
        actions={filteredActions}
        onStatusChange={updateActionStatus}
      />

      {/* Action Creation Modal */}
      <CreateActionModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSave={addAction}
      />
    </div>
  );
}
