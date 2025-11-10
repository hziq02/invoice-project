<script setup>
const authStore = useAuthStore()

onMounted(() => {
  // Initialize auth first
  authStore.initAuth()
  
  // Wait a bit to ensure initAuth completes
  // Then check authentication status
  setTimeout(() => {
    if (authStore.isAuthenticated && authStore.token) {
      navigateTo('/dashboard')
    } else {
      navigateTo('/login')
    }
  }, 100)
})
</script>

<template>
  <div></div>
</template>


