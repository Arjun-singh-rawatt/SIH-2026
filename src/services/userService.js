import { apiClient } from './api/apiClient';
import { mapUserFromApi } from './api/mappers';

export const userService = {
  /**
   * Fetch all active HSE officers and investigators
   */
  async getUsers() {
    const response = await apiClient.get('/users');
    return (response || []).map(mapUserFromApi);
  },

  /**
   * Fetch user profile by ID
   */
  async getUserById(userId) {
    if (!userId) return null;
    const response = await apiClient.get(`/users/${userId}`);
    return mapUserFromApi(response);
  },
};
