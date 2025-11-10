export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    user: null,
    refreshToken: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(username, password) {
      try {
        const config = useRuntimeConfig()
        const { access, refresh } = await $fetch(`${config.public.apiBase}/token/`, {
          method: 'POST',
          body: {
            username,
            password,
          },
        })

        this.token = access
        this.refreshToken = refresh
        
        // Store in localStorage
        if (process.client) {
          localStorage.setItem('token', access)
          localStorage.setItem('refreshToken', refresh)
        }

        return { success: true }
      } catch (error) {
        return { success: false, error: error.data?.detail || 'Login failed' }
      }
    },

    async logout() {
      this.token = null
      this.user = null
      this.refreshToken = null
      if (process.client) {
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        // Clear tracking session data
        localStorage.removeItem('session_id')
        // Clear sessionStorage (page tracking data)
        sessionStorage.clear()
      }
    },

    initAuth() {
      if (process.client) {
        const token = localStorage.getItem('token')
        if (token) {
          // Check if token is expired
          try {
            const payload = JSON.parse(atob(token.split('.')[1]))
            const exp = payload.exp * 1000 // Convert to milliseconds
            const now = Date.now()
            
            if (exp < now) {
              // Token expired - remove it
              console.warn('Token expired, removing from storage')
              localStorage.removeItem('token')
              localStorage.removeItem('refreshToken')
              this.token = null
              this.refreshToken = null
            } else {
              // Token is valid
              this.token = token
            }
          } catch (e) {
            // Invalid token format - remove it
            console.error('Invalid token format, removing from storage:', e)
            localStorage.removeItem('token')
            localStorage.removeItem('refreshToken')
            this.token = null
            this.refreshToken = null
          }
        }
        
        // Only set refresh token if we have a valid access token
        if (this.token) {
          const refresh = localStorage.getItem('refreshToken')
          if (refresh) {
            this.refreshToken = refresh
          }
        } else {
          // Clear refresh token if access token is invalid
          localStorage.removeItem('refreshToken')
          this.refreshToken = null
        }
      }
    },
  },
})

