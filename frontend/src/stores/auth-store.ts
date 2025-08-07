// stores/auth-store.ts
import { create } from 'zustand'
import { authApi, User } from '@/services/api'

interface AuthUser {
  id: string
  email: string
  name: string
}

interface AuthState {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  login: (credentials: { username: string; password: string }) => Promise<void>
  logout: () => void
  setToken: (token: string) => void
  setUser: (user: AuthUser) => void
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
          // Map API User to AuthUser
          const authUser: AuthUser = {
            id: userResponse.data.id.toString(),
            email: userResponse.data.email,
            name: `${userResponse.data.first_name} ${userResponse.data.last_name}`
          }
          get().setUser(authUser)
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
  
  setUser: (user: AuthUser) => {
    set({ user })
  },
  
  clearError: () => {
    set({ error: null })
  }
}))
