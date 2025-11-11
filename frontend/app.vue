<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
const authStore = useAuthStore()

// Import tracking functions
import { startSession, endSession, initEventTracking } from '~/src/utils/tracking/index.js'
import { useIdle } from '@vueuse/core' // For idle detection

const { idle } = useIdle(3 * 60 * 1000) // 3 minutes idle

onMounted(async () => {
  if (!process.client) {
    return
  }
  
  // Initialize auth first
  authStore.initAuth()
  
  // Initialize event-based tracking (beforeunload, visibilitychange)
  initEventTracking()
  
  // Start tracking ONLY if user is authenticated
  if (authStore.isAuthenticated && authStore.token) {
    // Wait a bit to ensure everything is loaded
    setTimeout(async () => {
      // Double check again before starting tracking
      if (authStore.isAuthenticated && authStore.token) {
        await startSession()
      }
    }, 100)
  }
})

// Watch for authentication changes
watch(() => authStore.isAuthenticated, (isAuthenticated, wasAuthenticated) => {
  if (!isAuthenticated && wasAuthenticated) {
    // User just logged out - end session
    endSession().catch(() => {})
    
    // Clear persistent flags
    if (process.client) {
      sessionStorage.removeItem('session_started')
      sessionStorage.removeItem('session_ended')
      sessionStorage.removeItem('current_page')
    }
  }
})

onBeforeUnmount(() => {
  // End session when component unmounts (user navigates away)
  if (process.client && authStore.isAuthenticated) {
    endSession().catch(() => {})
  }
})

// Watch idle state for session management
watch(idle, async (isIdle) => {
  // Only track if user is authenticated
  if (!process.client || !authStore.isAuthenticated || !authStore.token) {
    return
  }
  
  if (isIdle) {
    // User became idle - End current session
    await endSession()
  } else {
    // User became active again - Start new session
    // Clear flags first to allow new session
    sessionStorage.removeItem('session_started')
    sessionStorage.removeItem('session_ended')
    await startSession()
  }
})

</script>
