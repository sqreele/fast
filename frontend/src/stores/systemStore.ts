import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { systemApi } from '../services/api';

interface SystemState {
  healthStatus: string | null;
  maintenanceStatus: string | null;
  upscaleStatus: string | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setHealthStatus: (status: string | null) => void;
  setMaintenanceStatus: (status: string | null) => void;
  setUpscaleStatus: (status: string | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Async actions
  checkHealth: () => Promise<void>;
  performMaintenance: (action: 'start' | 'stop' | 'status') => Promise<void>;
  performUpscale: (resource: string, target: number) => Promise<void>;
}

export const useSystemStore = create<SystemState>()(
  devtools(
    (set) => ({
      healthStatus: null,
      maintenanceStatus: null,
      upscaleStatus: null,
      isLoading: false,
      error: null,
      
      setHealthStatus: (healthStatus) => set({ healthStatus }),
      setMaintenanceStatus: (maintenanceStatus) => set({ maintenanceStatus }),
      setUpscaleStatus: (upscaleStatus) => set({ upscaleStatus }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      
      checkHealth: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await systemApi.getHealth();
          set({ healthStatus: response.status, isLoading: false });
        } catch (error: any) {
          set({ error: error.message || 'Failed to check health', isLoading: false });
        }
      },
      
      performMaintenance: async (action) => {
        set({ isLoading: true, error: null });
        try {
          const response = await systemApi.maintenance(action);
          set({ maintenanceStatus: response.data.status, isLoading: false });
        } catch (error: any) {
          set({ error: error.message || 'Failed to perform maintenance', isLoading: false });
        }
      },
      
      performUpscale: async (resource, target) => {
        set({ isLoading: true, error: null });
        try {
          const response = await systemApi.upscale(resource, target);
          set({ upscaleStatus: response.data.status, isLoading: false });
        } catch (error: any) {
          set({ error: error.message || 'Failed to perform upscale', isLoading: false });
        }
      },
    }),
    { name: 'system-store' }
  )
);