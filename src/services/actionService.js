import { apiClient } from './api/apiClient';
import { mapActionFromApi, mapActionToApi } from './api/mappers';
import { mockActions } from '../data/mockActions';

export const actionService = {
  /**
   * Fetch paginated CAPA actions with multi-dimensional filtering
   */
  async getActions(filters = {}, page = 1, pageSize = 100) {
    const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';
    if (isDemo) {
      return mockActions.filter((a) => {
        if (filters.status && filters.status !== 'ALL' && a.status !== filters.status) return false;
        if (filters.priority && filters.priority !== 'ALL' && a.priority !== filters.priority) return false;
        if (filters.facilityId && filters.facilityId !== 'ALL' && a.facilityId !== filters.facilityId) return false;
        return true;
      });
    }

    try {
      const queryParams = {
        page,
        page_size: pageSize,
        search: filters.search,
        status: filters.status,
        priority: filters.priority,
        facility_id: filters.facilityId,
        assigned_to: filters.assignedTo,
        report_id: filters.reportId,
      };

      const response = await apiClient.get('/actions', queryParams);
      if (response && response.items) {
        return response.items.map(mapActionFromApi);
      }
      if (Array.isArray(response)) {
        return response.map(mapActionFromApi);
      }
      return [];
    } catch (error) {
      console.warn('Backend API failed for getActions. Using demo data.');
      return mockActions;
    }
  },

  /**
   * Fetch single action by ID
   */
  async getActionById(actionId) {
    if (!actionId) return null;
    const isDemo = import.meta.env.VITE_DEMO_MODE === 'true';
    if (isDemo) {
      return mockActions.find((a) => a.actionId === actionId || a.id === actionId) || null;
    }
    try {
      const response = await apiClient.get(`/actions/${actionId}`);
      return mapActionFromApi(response);
    } catch (error) {
      console.warn('Backend API failed for getActionById. Using demo data.');
      return mockActions.find((a) => a.actionId === actionId || a.id === actionId) || null;
    }
  },

  /**
   * Update action status (e.g. Open -> In Progress -> Completed)
   */
  async updateActionStatus(actionId, newStatus) {
    const response = await apiClient.patch(`/actions/${actionId}`, { status: newStatus });
    return mapActionFromApi(response);
  },

  /**
   * Create and assign a new CAPA action item
   */
  async createAction(actionData) {
    const payload = mapActionToApi(actionData);
    const response = await apiClient.post('/actions', payload);
    return mapActionFromApi(response);
  },

  /**
   * Delete an action item
   */
  async deleteAction(actionId) {
    return apiClient.delete(`/actions/${actionId}`);
  },

  /**
   * Fetch overall action statistics counters
   */
  async getActionStats() {
    const response = await apiClient.get('/actions/stats');
    return {
      total: response.total,
      open: response.open,
      inProgress: response.in_progress,
      completed: response.completed,
      overdue: response.overdue,
    };
  },
};
