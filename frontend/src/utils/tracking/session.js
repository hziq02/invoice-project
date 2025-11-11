/**
 * Session tracking functions
 * Handles session start and end
 */

import { getOrCreateSessionId, getUserId, trackingRequest } from './helpers.js'

/**
 * End session synchronously (for browser close events)
 * Uses sendBeacon or synchronous XHR for reliable delivery
 * @returns {boolean} True if successful, false otherwise
 */
export function endSessionSync() {
  if (!process.client) return false
  
  const sessionId = getOrCreateSessionId()
  const userId = getUserId()
  
  if (!sessionId || !userId) {
    return false
  }
  
  const sessionEnded = sessionStorage.getItem('session_ended')
  if (sessionEnded === 'true') {
    return false
  }
  
  const endTime = new Date().toISOString()
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  const token = authStore.token
  
  if (!token) {
    return false
  }
  
  const url = `${config.public.apiBase}/track/session/end`
  const data = JSON.stringify({
    session_id: sessionId,
    user_id: userId,
    end_time: endTime,
    token: token
  })
  
  if (navigator.sendBeacon) {
    const blob = new Blob([data], { type: 'application/json' })
    const success = navigator.sendBeacon(url, blob)
    
    if (success) {
      sessionStorage.setItem('session_ended', 'true')
      return true
    }
  }
  
  try {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', url, false)
    xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    xhr.send(data)
    
    if (xhr.status >= 200 && xhr.status < 300) {
      sessionStorage.setItem('session_ended', 'true')
      return true
    }
  } catch (e) {
    // Silent fail
  }
  
  return false
}

/**
 * End session (async version for normal use)
 * Called on logout, navigate away, or visibility change
 */
export async function endSession() {
  if (!process.client) return
  
  const sessionId = getOrCreateSessionId()
  const userId = getUserId()
  
  if (!sessionId || !userId) {
    return
  }
  
  const sessionEnded = sessionStorage.getItem('session_ended')
  if (sessionEnded === 'true') {
    return
  }
  
  const endTime = new Date().toISOString()
  
  try {
    const config = useRuntimeConfig()
    const authStore = useAuthStore()
    const token = authStore.token
    
    if (!token) {
      console.warn('No token available for ending session')
      return
    }
    
    const url = `${config.public.apiBase}/track/session/end`
    const data = {
      session_id: sessionId,
      user_id: userId,
      end_time: endTime
    }
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data),
      keepalive: true
    })
    
    if (response.ok) {
      sessionStorage.setItem('session_ended', 'true')
    }
  } catch (error) {
    console.error('Error ending session:', error)
  }
}

/**
 * Start a new session when user opens the app
 * Called once when app loads
 * Uses persistent flag to prevent multiple calls
 */
export async function startSession() {
  if (!process.client) {
    return
  }
  
  const sessionId = getOrCreateSessionId()
  const userId = getUserId()
  
  if (!sessionId || !userId) {
    return
  }
  
  const sessionEnded = sessionStorage.getItem('session_ended')
  if (sessionEnded === 'true') {
    sessionStorage.removeItem('session_ended')
    sessionStorage.removeItem('session_started')
  }
  
  const sessionStarted = sessionStorage.getItem('session_started')
  if (sessionStarted === 'true') {
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
      sessionStorage.setItem('session_started', 'true')
      sessionStorage.removeItem('session_ended')
    }
  } catch (error) {
    console.error('Error starting session:', error)
  }
}

