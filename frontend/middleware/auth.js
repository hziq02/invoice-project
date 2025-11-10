import { startPageEvent, endPageEvent } from '~/src/utils/tracking'

export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()
  
  // IMPORTANT: Check authentication FIRST before any tracking
  if (!authStore.isAuthenticated) {
    return navigateTo('/login')
  }
  
  // Only track page navigation if user is authenticated AND on client side
  // Skip tracking for login page and root path
  if (process.client && to.path !== '/login' && to.path !== '/') {
    // End previous page event (if coming from another page)
    // Only if coming from a valid page (not login, not root)
    if (from.path && from.path !== to.path && from.path !== '/' && from.path !== '/login') {
      endPageEvent(from.path)
    }
    
    // Start new page event (always start, even if coming from root or login)
    // This ensures first page load is tracked
    // Use setTimeout to ensure it runs after navigation
    setTimeout(() => {
      startPageEvent(to.path)
    }, 100)
  }
})

