/**
 * Browser event tracking initialization
 * Sets up listeners for beforeunload, unload, visibilitychange
 */

import { endSession, endSessionSync } from './session.js'
import { endPageEventSync, getCurrentPageForEvents } from './pageEvent.js'

/**
 * Initialize event-based tracking
 * Sets up listeners for beforeunload, visibilitychange, etc.
 */
export function initEventTracking() {
  if (!process.client) return
  
  window.addEventListener('unload', () => {
    const currentPage = getCurrentPageForEvents()
    if (currentPage) {
      endPageEventSync(currentPage)
    }
    endSessionSync()
  })
  
  window.addEventListener('beforeunload', () => {
    const currentPage = getCurrentPageForEvents()
    if (currentPage) {
      endPageEventSync(currentPage)
    }
    endSessionSync()
  })
  
  // Handle visibility change (tab hidden/visible)
  let hiddenStartTime = null
  const VISIBILITY_THRESHOLD = 2 * 60 * 1000 // 2 minutes in milliseconds
  
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      hiddenStartTime = Date.now()
    } else {
      if (hiddenStartTime) {
        const hiddenDuration = Date.now() - hiddenStartTime
        if (hiddenDuration > VISIBILITY_THRESHOLD) {
          endSession().catch(() => {})
          sessionStorage.removeItem('session_started')
          sessionStorage.removeItem('session_ended')
        }
        hiddenStartTime = null
      }
    }
  })
}

