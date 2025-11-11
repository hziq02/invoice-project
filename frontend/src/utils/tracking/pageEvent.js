/**
 * Page event tracking functions
 * Handles page navigation tracking
 */

import { getOrCreateSessionId, getUserId, trackingRequest } from './helpers.js'

/**
 * Get current active page from sessionStorage
 */
function getCurrentPage() {
  if (!process.client) return null
  return sessionStorage.getItem('current_page')
}

/**
 * Set current active page in sessionStorage
 */
function setCurrentPage(page) {
  if (!process.client) return
  sessionStorage.setItem('current_page', page)
}

/**
 * End page event synchronously (for browser close events)
 * Uses sendBeacon or synchronous XHR for reliable delivery
 * @param {string} page - Page path
 * @returns {boolean} True if successful, false otherwise
 */
export function endPageEventSync(page) {
  if (!process.client || !page) return false
  
  const sessionId = getOrCreateSessionId()
  const userId = getUserId()
  
  if (!sessionId || !userId) {
    return false
  }
  
  const pageStartTime = sessionStorage.getItem(`page_start_${page}`)
  if (!pageStartTime) {
    return false
  }
  
  const endTime = new Date().toISOString()
  const startTimeObj = new Date(pageStartTime)
  const endTimeObj = new Date(endTime)
  const duration = Math.floor((endTimeObj - startTimeObj) / 1000)
  
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  const token = authStore.token
  
  if (!token) {
    return false
  }
  
  const url = `${config.public.apiBase}/track/event/end`
  const data = JSON.stringify({
    session_id: sessionId,
    user_id: userId,
    page: page,
    end_time: endTime,
    duration: duration,
    token: token
  })
  
  // Use sendBeacon
  if (navigator.sendBeacon) {
    const blob = new Blob([data], { type: 'application/json' })
    const success = navigator.sendBeacon(url, blob)
    if (success) {
      sessionStorage.removeItem(`page_start_${page}`)
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
      sessionStorage.removeItem(`page_start_${page}`)
      return true
    }
  } catch (e) {
    // Silent fail
  }
  
  return false
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
  const pageStartTime = sessionStorage.getItem(`page_start_${page}`)
  
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
  
  sessionStorage.removeItem(`page_start_${page}`)
}

/**
 * Track when user enters a page
 * @param {string} page - Page path (e.g., "/dashboard")
 */
export async function startPageEvent(page) {
  if (!process.client) return
  
  const currentPage = getCurrentPage()
  if (currentPage && currentPage !== page) {
    await endPageEvent(currentPage).catch(() => {})
  } else if (currentPage === page) {
    await endPageEvent(page).catch(() => {})
  }
  
  const sessionId = getOrCreateSessionId()
  const userId = getUserId()
  
  if (!sessionId || !userId) {
    console.warn('Cannot start page event: missing sessionId or userId', { sessionId, userId, page })
    return
  }
  
  const startTime = new Date().toISOString()
  sessionStorage.setItem(`page_start_${page}`, startTime)
  setCurrentPage(page)
  
  try {
    const response = await trackingRequest('event/start', {
      session_id: sessionId,
      user_id: userId,
      page: page,
      start_time: startTime
    })
    
  } catch (error) {
    console.error('Error starting page event:', error, page)
  }
}

/**
 * Get current page (exported for use in events.js)
 */
export function getCurrentPageForEvents() {
  return getCurrentPage()
}

