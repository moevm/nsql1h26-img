<script setup lang="ts">
import TopNav from '@/layout/TopNav.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-canvas">
    <TopNav />
    <main class="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
      <slot />
    </main>
  </div>
</template>
