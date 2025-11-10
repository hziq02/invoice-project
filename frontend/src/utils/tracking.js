/**
 * User Tracking System

 * Generate a unique session ID (UUID)
 * Stores it in localStorage so it persists across page reloads
 */
function getOrCreateSessionId() {
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
function getUserId() {
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
 * Get API base URL from config
 */
function getApiBase() {
  const config = useRuntimeConfig()
  return config.public.apiBase
}

/**
 * Make authenticated API request
 */
async function trackingRequest(endpoint, data) {
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
      // Clear expired token
      authStore.logout()
      return null
    }
  } catch (e) {
    console.warn('Invalid token, skipping tracking request')
    return null
  }
  
  try {
    const response = await $fetch(`${getApiBase()}/track/${endpoint}`, {
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

// ========== MAIN TRACKING FUNCTIONS ==========

/**
 * Start a new session when user opens the app
 * Called once when app loads
 */
export async function startSession() {
  if (!process.client) {
    console.warn('startSession: Not on client side')
    return
  }
  
  const sessionId = getOrCreateSessionId()
  const userId = getUserId()
  
  if (!sessionId || !userId) {
    console.warn('Cannot start session: missing sessionId or userId', { sessionId, userId })
    return
  }
  
  const startTime = new Date().toISOString()
  
  try {
    const response = await trackingRequest('session/start', {
      session_id: sessionId,
      user_id: userId,
      start_time: startTime
    })
    
    if (response) {
      console.log('✅ Session started successfully:', sessionId)
    } else {
      console.warn('⚠️ Session start returned null (may have failed silently)')
    }
  } catch (error) {
    console.error('❌ Error starting session:', error)
  }
}

/**
 * Track when user enters a page
 * @param {string} page - Page path (e.g., "/dashboard")
 */
export async function startPageEvent(page) {
  if (!process.client) {
    console.warn('startPageEvent: Not on client side')
    return
  }
  
  const sessionId = getOrCreateSessionId()
  const userId = getUserId()
  
  if (!sessionId || !userId) {
    console.warn('Cannot start page event: missing sessionId or userId', { sessionId, userId, page })
    return
  }
  
  const startTime = new Date().toISOString()
  
  // Store page start time locally to calculate duration later
  if (process.client) {
    sessionStorage.setItem(`page_start_${page}`, startTime)
  }
  
  try {
    const response = await trackingRequest('event/start', {
      session_id: sessionId,
      user_id: userId,
      page: page,
      start_time: startTime
    })
    
    if (response) {
      console.log('✅ Page event started:', page)
    } else {
      console.warn('⚠️ Page event start returned null (may have failed silently)', page)
    }
  } catch (error) {
    console.error('❌ Error starting page event:', error, page)
  }
}

/**
 * Track when user leaves a page
 * @param {string} page - Page path (e.g., "/dashboard")
 */
export async function endPageEvent(page) {
  if (!process.client) return
  
  const sessionId = getOrCreateSessionId()
  const userId = getUserId()
  
  if (!sessionId || !userId) {
    return
  }
  
  // Get page start time from sessionStorage
  const pageStartTime = process.client ? sessionStorage.getItem(`page_start_${page}`) : null
  
  if (!pageStartTime) {
    console.warn(`No start time found for page: ${page}`)
    return
  }
  
  const endTime = new Date().toISOString()
  const startTimeObj = new Date(pageStartTime)
  const endTimeObj = new Date(endTime)
  const duration = Math.floor((endTimeObj - startTimeObj) / 1000) // Duration in seconds
  
  await trackingRequest('event/end', {
    session_id: sessionId,
    user_id: userId,
    page: page,
    end_time: endTime,
    duration: duration
  })
  
  // Clean up
  if (process.client) {
    sessionStorage.removeItem(`page_start_${page}`)
  }
  
  console.log(`Page event ended: ${page} (${duration}s)`)
}

/**
 * Heartbeat - ping server every 5 minutes to show user is active
 * Returns the interval ID so you can clear it later if needed
 */
export function startHeartbeat() {
  if (!process.client) return null
  
  const sessionId = getOrCreateSessionId()
  const userId = getUserId()
  
  if (!sessionId || !userId) {
    return null
  }
  
  // Send ping immediately
  const sendPing = async () => {
    await trackingRequest('ping', {
      session_id: sessionId,
      user_id: userId,
      timestamp: new Date().toISOString()
    })
    console.log('Heartbeat ping sent')
  }
  
  // Send first ping
  sendPing()
  
  // Change 300000 to adjust interval: 60000=1min, 120000=2min, 300000=5min, 600000=10min
  const intervalId = setInterval(sendPing, 60000)
  
  return intervalId
}

/**
 * Stop heartbeat (cleanup function)
 * @param {number} intervalId - Interval ID returned from startHeartbeat()
 */
export function stopHeartbeat(intervalId) {
  if (intervalId && process.client) {
    clearInterval(intervalId)
    console.log('Heartbeat stopped')
  }
}