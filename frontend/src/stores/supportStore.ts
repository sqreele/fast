import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { SupportTicket, supportApi } from '../services/api';

interface SupportState {
  tickets: SupportTicket[];
  currentTicket: SupportTicket | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setTickets: (tickets: SupportTicket[]) => void;
  setCurrentTicket: (ticket: SupportTicket | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Async actions
  fetchTickets: () => Promise<void>;
  fetchTicket: (id: string) => Promise<void>;
  createTicket: (data: Omit<SupportTicket, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
  updateTicket: (id: string, data: Partial<SupportTicket>) => Promise<void>;
}

export const useSupportStore = create<SupportState>()(
  devtools(
    (set, get) => ({
      tickets: [],
      currentTicket: null,
      isLoading: false,
      error: null,
      
      setTickets: (tickets) => set({ tickets }),
      setCurrentTicket: (currentTicket) => set({ currentTicket }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      
      fetchTickets: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await supportApi.getTickets();
          set({ tickets: response.data, isLoading: false });
        } catch (error: any) {
          set({ error: error.message || 'Failed to fetch tickets', isLoading: false });
        }
      },
      
      fetchTicket: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await supportApi.getTicket(id);
          set({ currentTicket: response.data, isLoading: false });
        } catch (error: any) {
          set({ error: error.message || 'Failed to fetch ticket', isLoading: false });
        }
      },
      
      createTicket: async (data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await supportApi.createTicket(data);
          const { tickets } = get();
          set({ 
            tickets: [...tickets, response.data], 
            isLoading: false 
          });
        } catch (error: any) {
          set({ error: error.message || 'Failed to create ticket', isLoading: false });
        }
      },
      
      updateTicket: async (id: string, data) => {
        set({ isLoading: true, error: null });
        try {
          const response = await supportApi.updateTicket(id, data);
          const { tickets } = get();
          set({
            tickets: tickets.map(t => t.id === id ? response.data : t),
            currentTicket: response.data,
            isLoading: false
          });
        } catch (error: any) {
          set({ error: error.message || 'Failed to update ticket', isLoading: false });
        }
      },
    }),
    { name: 'support-store' }
  )
);