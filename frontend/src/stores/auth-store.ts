// stores/auth-store.ts
import { create } from 'zustand'
import { authApi } from '@/services/api'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  phone?: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  login: (credentials: { username: string; password: string }) => Promise<void>
  logout: () => void
  setToken: (token: string) => void
  setUser: (user: User) => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  loading: false,
  error: null,
  
  login: async (credentials) => {
    const state = get()
    if (state.loading) throw new Error('Login already in progress')
    
    set({ loading: true, error: null })
    try {
      const loginResponse = await authApi.login(credentials)
      if (loginResponse.success) {
        get().setToken(loginResponse.data.token)
        
        // Get user data
        const userResponse = await authApi.me()
        if (userResponse.success) {
          get().setUser(userResponse.data)
        }
      }
    } catch (error: any) {
      const errorMessage = error?.message || 'Login failed'
      set({ 
        error: errorMessage, 
        token: null, 
        user: null, 
        isAuthenticated: false 
      })
      throw error
    } finally {
      set({ loading: false })
    }
  },
  
  logout: () => {
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null
    })
  },
  
  setToken: (token: string) => {
    set({ token, isAuthenticated: true })
  },
  
  setUser: (user: User) => {
    set({ user })
  },
  
  clearError: () => {
    set({ error: null })
  }
}))
