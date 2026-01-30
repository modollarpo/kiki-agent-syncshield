// --- Profile API ---
export const fetchProfile = async () => {
  const res = await api.get('/profile');
  return res.data;
};

export const updateProfile = async (data: { name?: string; avatarUrl?: string; email?: string }) => {
  return api.patch('/profile', data);
};

// --- Billing API ---
export const fetchBilling = async () => {
  const res = await api.get('/billing');
  return res.data;
};

export const updateBilling = async (data: { cardToken?: string; plan?: string }) => {
  return api.patch('/billing', data);
};

export const exportBillingData = async () => {
  const res = await api.get('/billing/export', { responseType: 'blob' });
  return res.data;
};

// --- Notification Settings API ---
export const fetchNotificationSettings = async () => {
  const res = await api.get('/notifications/settings');
  return res.data;
};

export const updateNotificationSettings = async (data: any) => {
  return api.patch('/notifications/settings', data);
};

// --- Real-time Notifications (WebSocket) ---
export const getNotificationSocket = () => {
  return new WebSocket(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:3001/ws/notifications');
};
// --- Notifications API ---
export const fetchNotifications = async (params?: { unreadOnly?: boolean; page?: number; pageSize?: number }) => {
  const res = await api.get('/notifications', { params });
  return res.data;
};

export const markNotificationRead = async (notificationId: string) => {
  return api.patch(`/notifications/${notificationId}/read`);
};

export const deleteNotification = async (notificationId: string) => {
  return api.delete(`/notifications/${notificationId}`);
};
// --- Audit Logs API ---
export const fetchAuditLogs = async (params?: { userId?: string; action?: string; page?: number; pageSize?: number }) => {
  const res = await api.get('/audit/logs', { params });
  return res.data;
};
// --- Team Members API ---
export const fetchTeamMembers = async (teamId: string) => {
  const res = await api.get(`/teams/${teamId}/members`);
  return res.data;
};

export const addTeamMember = async (teamId: string, userId: string, role: string) => {
  return api.post(`/teams/${teamId}/members`, { userId, role });
};

export const removeTeamMember = async (teamId: string, userId: string) => {
  return api.delete(`/teams/${teamId}/members/${userId}`);
};

export const updateTeamMemberRole = async (teamId: string, userId: string, role: string) => {
  return api.patch(`/teams/${teamId}/members/${userId}`, { role });
};
// --- Teams API ---
export const fetchTeams = async () => {
  const res = await api.get('/teams');
  return res.data;
};

export const addTeam = async (name: string) => {
  return api.post('/teams', { name });
};

export const removeTeam = async (teamId: string) => {
  return api.delete(`/teams/${teamId}`);
};

export const updateTeam = async (teamId: string, data: { name?: string }) => {
  return api.patch(`/teams/${teamId}`, data);
};
// src/utils/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  withCredentials: true,
});

export interface ApiUser {
  id: string;
  name: string;
  email: string;
  role: string;
  avatarUrl?: string;
}

export const fetchCurrentUser = async (): Promise<ApiUser | null> => {
  try {
    const res = await api.get('/auth/me');
    return res.data;
  } catch (e) {
    return null;
  }
};

export const login = async (email: string, password: string) => {
  return api.post('/auth/login', { email, password });
};

export const logout = async () => {
  return api.post('/auth/logout');
};

export const inviteUser = async (email: string, role: string) => {
  return api.post('/users/invite', { email, role });
};

export const removeUser = async (userId: string) => {
  return api.delete(`/users/${userId}`);
};

export default api;
