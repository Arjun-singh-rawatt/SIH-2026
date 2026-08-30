import { apiClient } from './api/apiClient';
import { mapActionFromApi, mapActionToApi } from './api/mappers';

export const actionService = {
  /**
   * Fetch paginated CAPA actions with multi-dimensional filtering
   */
  async getActions(filters = {}, page = 1, pageSize = 100) {
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
  },

  /**
   * Fetch single action by ID
   */
  async getActionById(actionId) {
    if (!actionId) return null;
    const response = await apiClient.get(`/actions/${actionId}`);
    return mapActionFromApi(response);
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
