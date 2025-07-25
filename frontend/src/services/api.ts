import api from '../lib/axios';
import { AxiosResponse } from 'axios';

// Types
export interface User {
  id: string;
  username: string;
  email: string;
  name: string;
  role: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'on-hold';
  priority: 'low' | 'medium' | 'high';
  createdAt: string;
  updatedAt: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  assignedTo?: string;
  projectId: string;
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SupportTicket {
  id: string;
  title: string;
  description: string;
  status: 'open' | 'in-progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  createdBy: string;
  assignedTo?: string;
  createdAt: string;
  updatedAt: string;
}

// API Response wrapper
interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

// Auth API
export const authApi = {
  login: async (credentials: { username: string; password: string }) => {
    const response: AxiosResponse<ApiResponse<{ user: User; token: string }>> = 
      await api.post('/api/v1/auth/login', credentials);
    return response.data;
  },
  
  me: async () => {
    const response: AxiosResponse<ApiResponse<User>> = await api.get('/api/v1/auth/me');
    return response.data;
  },
  
  logout: async () => {
    const response: AxiosResponse<ApiResponse<null>> = await api.post('/api/v1/auth/logout');
    return response.data;
  }
};

// Users API
export const usersApi = {
  getUsers: async () => {
    const response: AxiosResponse<ApiResponse<User[]>> = await api.get('/users');
    return response.data;
  },
  
  getUser: async (id: string) => {
    const response: AxiosResponse<ApiResponse<User>> = await api.get(`/users/${id}`);
    return response.data;
  },
  
  updateUser: async (id: string, data: Partial<User>) => {
    const response: AxiosResponse<ApiResponse<User>> = await api.put(`/users/${id}`, data);
    return response.data;
  }
};

// Projects API
export const projectsApi = {
  getProjects: async () => {
    const response: AxiosResponse<ApiResponse<Project[]>> = await api.get('/projects');
    return response.data;
  },
  
  getProject: async (id: string) => {
    const response: AxiosResponse<ApiResponse<Project>> = await api.get(`/projects/${id}`);
    return response.data;
  },
  
  createProject: async (data: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>) => {
    const response: AxiosResponse<ApiResponse<Project>> = await api.post('/projects', data);
    return response.data;
  },
  
  updateProject: async (id: string, data: Partial<Project>) => {
    const response: AxiosResponse<ApiResponse<Project>> = await api.put(`/projects/${id}`, data);
    return response.data;
  },
  
  deleteProject: async (id: string) => {
    const response: AxiosResponse<ApiResponse<null>> = await api.delete(`/projects/${id}`);
    return response.data;
  }
};

// Tasks API
export const tasksApi = {
  getTasks: async (projectId?: string) => {
    const url = projectId ? `/tasks?projectId=${projectId}` : '/tasks';
    const response: AxiosResponse<ApiResponse<Task[]>> = await api.get(url);
    return response.data;
  },
  
  getTask: async (id: string) => {
    const response: AxiosResponse<ApiResponse<Task>> = await api.get(`/tasks/${id}`);
    return response.data;
  },
  
  createTask: async (data: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => {
    const response: AxiosResponse<ApiResponse<Task>> = await api.post('/tasks', data);
    return response.data;
  },
  
  updateTask: async (id: string, data: Partial<Task>) => {
    const response: AxiosResponse<ApiResponse<Task>> = await api.put(`/tasks/${id}`, data);
    return response.data;
  },
  
  deleteTask: async (id: string) => {
    const response: AxiosResponse<ApiResponse<null>> = await api.delete(`/tasks/${id}`);
    return response.data;
  }
};

// Support API
export const supportApi = {
  getTickets: async () => {
    const response: AxiosResponse<ApiResponse<SupportTicket[]>> = await api.get('/support/tickets');
    return response.data;
  },
  
  getTicket: async (id: string) => {
    const response: AxiosResponse<ApiResponse<SupportTicket>> = await api.get(`/support/tickets/${id}`);
    return response.data;
  },
  
  createTicket: async (data: Omit<SupportTicket, 'id' | 'createdAt' | 'updatedAt'>) => {
    const response: AxiosResponse<ApiResponse<SupportTicket>> = await api.post('/support/tickets', data);
    return response.data;
  },
  
  updateTicket: async (id: string, data: Partial<SupportTicket>) => {
    const response: AxiosResponse<ApiResponse<SupportTicket>> = await api.put(`/support/tickets/${id}`, data);
    return response.data;
  }
};

// System API
export const systemApi = {
  getHealth: async () => {
    const response: AxiosResponse<{ status: string; timestamp: string }> = await api.get('/health');
    return response.data;
  },
  
  maintenance: async (action: 'start' | 'stop' | 'status') => {
    const response: AxiosResponse<ApiResponse<{ status: string; message: string }>> = 
      await api.post('/system/maintenance', { action });
    return response.data;
  },
  
  upscale: async (resource: string, target: number) => {
    const response: AxiosResponse<ApiResponse<{ status: string; details: Record<string, unknown> }>> = 
      await api.post('/system/upscale', { resource, target });
    return response.data;
  }
};