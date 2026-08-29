import { mockActions } from '../data/mockActions';

let inMemoryActions = [...mockActions];

export const actionService = {
  async getActions(filters = {}) {
    await new Promise((resolve) => setTimeout(resolve, 30));
    let result = [...inMemoryActions];

    if (filters.search) {
      const q = filters.search.toLowerCase();
      result = result.filter(
        (a) =>
          a.actionId.toLowerCase().includes(q) ||
          a.reportTitle.toLowerCase().includes(q) ||
          a.description.toLowerCase().includes(q) ||
          a.assigneeName.toLowerCase().includes(q) ||
          a.facilityName.toLowerCase().includes(q)
      );
    }

    if (filters.status && filters.status !== 'ALL') {
      result = result.filter((a) => a.status === filters.status);
    }

    if (filters.priority && filters.priority !== 'ALL') {
      result = result.filter((a) => a.priority === filters.priority);
    }

    if (filters.facilityId && filters.facilityId !== 'ALL') {
      result = result.filter((a) => a.facilityId === filters.facilityId);
    }

    if (filters.reportId) {
      result = result.filter((a) => a.reportId.toUpperCase() === filters.reportId.toUpperCase());
    }

    return result;
  },

  async getActionById(actionId) {
    await new Promise((resolve) => setTimeout(resolve, 20));
    return inMemoryActions.find((a) => a.actionId === actionId) || null;
  },

  async updateActionStatus(actionId, newStatus) {
    await new Promise((resolve) => setTimeout(resolve, 30));
    const index = inMemoryActions.findIndex((a) => a.actionId === actionId);
    if (index !== -1) {
      inMemoryActions[index] = {
        ...inMemoryActions[index],
        status: newStatus,
        completedAt: newStatus === 'Completed' ? new Date().toISOString() : inMemoryActions[index].completedAt,
      };
      return inMemoryActions[index];
    }
    throw new Error('Action not found');
  },

  async createAction(actionData) {
    await new Promise((resolve) => setTimeout(resolve, 40));
    const newSeq = 80 + inMemoryActions.length + 1;
    const newAction = {
      actionId: `ACT-2026-0${newSeq}`,
      createdAt: new Date().toISOString(),
      status: 'Open',
      completedAt: null,
      ...actionData,
    };
    inMemoryActions.unshift(newAction);
    return newAction;
  },

  getActionStats() {
    const total = inMemoryActions.length;
    const open = inMemoryActions.filter((a) => a.status === 'Open').length;
    const inProgress = inMemoryActions.filter((a) => a.status === 'In Progress').length;
    const completed = inMemoryActions.filter((a) => a.status === 'Completed').length;
    const overdue = inMemoryActions.filter((a) => a.status === 'Overdue').length;

    return { total, open, inProgress, completed, overdue };
  },
};
