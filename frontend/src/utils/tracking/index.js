/**
 * Tracking System - Main Export File
 * 
 * This file re-exports all tracking functions for easy importing
 * 
 * Usage:
 *   import { startSession, endSession, startPageEvent } from '~/src/utils/tracking'
 */

// Session functions
export { startSession, endSession, endSessionSync } from './session.js'

// Page event functions
export { startPageEvent, endPageEvent, endPageEventSync } from './pageEvent.js'

// Event tracking initialization
export { initEventTracking } from './events.js'

