<template>
  <div>
    <NuxtPage />
  </div>
</template>

<script setup>
const authStore = useAuthStore()

// Import tracking functions
import { startSession, startHeartbeat, stopHeartbeat } from '~/src/utils/tracking'

let heartbeatInterval = null

onMounted(async () => {
  // Initialize auth first
  authStore.initAuth()
  
  // Start tracking ONLY if user is authenticated
  // Double check to ensure token exists and is valid
  if (process.client && authStore.isAuthenticated && authStore.token) {
    // Wait a bit to ensure everything is loaded
    setTimeout(async () => {
      // Double check again before starting tracking
      if (authStore.isAuthenticated && authStore.token) {
        // IMPORTANT: Wait for session to be created before starting heartbeat
        await startSession()  // Create new session in database (wait for it to complete)
        heartbeatInterval = startHeartbeat()  // Start pinging every 1 minute
      }
    }, 500)
  }
})

// Watch for authentication changes
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (!isAuthenticated) {
    // User logged out or token invalid - stop heartbeat
    if (heartbeatInterval) {
      stopHeartbeat(heartbeatInterval)
      heartbeatInterval = null
    }
  }
})

onUnmounted(() => {
  // Clean up heartbeat when app closes
  if (heartbeatInterval) {
    stopHeartbeat(heartbeatInterval)
    heartbeatInterval = null
  }
})
</script>


