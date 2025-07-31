import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { Project, projectsApi } from '../services/api';
import { handleApiError } from '../lib/axios';

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // Async actions
  fetchProjects: () => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (data: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
  updateProject: (id: string, data: Partial<Project>) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
}

export const useProjectStore = create<ProjectState>()(
  devtools(
    (set, get) => ({
      projects: [],
      currentProject: null,
      isLoading: false,
      error: null,
      
      setProjects: (projects) => set({ projects }),
      setCurrentProject: (currentProject) => set({ currentProject }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),
      
      fetchProjects: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await projectsApi.getProjects();
          set({ projects: response.data, isLoading: false });
        } catch (error: unknown) {
          const errorMessage = handleApiError(error);
          set({ error: errorMessage, isLoading: false });
        }
      },
      
      fetchProject: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await projectsApi.getProject(id);
          set({ currentProject: response.data, isLoading: false });
        } catch (error: unknown) {
          const errorMessage = handleApiError(error);
          set({ error: errorMessage, isLoading: false });
        }
      },
      
      createProject: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await projectsApi.createProject(data);
          const { projects } = get();
          set({ 
            projects: [...projects, response.data], 
            isLoading: false 
          });
        } catch (error: unknown) {
          const errorMessage = handleApiError(error);
          set({ error: errorMessage, isLoading: false });
        }
      },
      
      updateProject: async (id: string, data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await projectsApi.updateProject(id, data);
          const { projects } = get();
          set({
            projects: projects.map(p => p.id === id ? response.data : p),
            currentProject: response.data,
            isLoading: false
          });
        } catch (error: unknown) {
          const errorMessage = handleApiError(error);
          set({ error: errorMessage, isLoading: false });
        }
      },
      
      deleteProject: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          await projectsApi.deleteProject(id);
          const { projects } = get();
          set({
            projects: projects.filter(p => p.id !== id),
            currentProject: null,
            isLoading: false
          });
        } catch (error: unknown) {
          const errorMessage = handleApiError(error);
          set({ error: errorMessage, isLoading: false });
        }
      },
    }),
    { name: 'project-store' }
  )
);