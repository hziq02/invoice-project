/**
 * Helper functions for tracking system
 * Utility functions used by other tracking modules
 */

/**
 * Generate a unique session ID (UUID)
 * Stores it in localStorage so it persists across page reloads
 */
export function getOrCreateSessionId() {
  if (process.client) {
    let sessionId = localStorage.getItem('session_id')
    
    if (!sessionId) {
      // Generate UUID v4
      sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0
        const v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
      localStorage.setItem('session_id', sessionId)
    }
    
    return sessionId
  }
  return null
}

/**
 * Get current user ID from JWT token
 * Decodes the token to extract user_id
 */
export function getUserId() {
  if (process.client) {
    const authStore = useAuthStore()
    const token = authStore.token
    
    if (token) {
      try {
        // JWT token format: header.payload.signature
        // We need to decode the payload
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.user_id || payload.sub || payload.id || null // Check multiple possible fields
      } catch (e) {
        console.error('Error decoding token:', e)
        return null
      }
    }
  }
  return null
}

/**
 * Make authenticated API request
 * @param {string} endpoint - API endpoint (e.g., "session/start")
 * @param {object} data - Request data
 * @returns {Promise<object|null>} Response data or null if failed
 */
export async function trackingRequest(endpoint, data) {
  const authStore = useAuthStore()
  const token = authStore.token
  
  if (!token) {
    console.warn('No auth token, skipping tracking request')
    return null
  }
  
  // Validate token is not expired
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp * 1000
    const now = Date.now()
    
    if (exp < now) {
      console.warn('Token expired, skipping tracking request')
      authStore.logout()
      return null
    }
  } catch (e) {
    console.warn('Invalid token, skipping tracking request')
    return null
  }
  
  try {
    const config = useRuntimeConfig()
    const response = await $fetch(`${config.public.apiBase}/track/${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: data
    })
    return response
  } catch (error) {
    // If 401, token is invalid - logout user
    if (error.status === 401 || error.statusCode === 401) {
      console.warn('Unauthorized (401) in tracking request, logging out')
      authStore.logout()
      navigateTo('/login')
      return null
    }
    console.error(`Tracking error (${endpoint}):`, error)
    // Don't throw - tracking failures shouldn't break the app
    return null
  }
}

