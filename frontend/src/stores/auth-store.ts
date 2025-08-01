// stores/auth-store.ts
import { authApi } from '@/services/api'

// In your login method:
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
