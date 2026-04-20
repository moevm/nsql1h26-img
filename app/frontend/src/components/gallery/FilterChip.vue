<script setup lang="ts">
defineProps<{ label: string }>()
const emit = defineEmits<{ remove: [] }>()
</script>

<template>
  <span class="inline-flex items-center gap-1 rounded-full bg-neutral-900 px-3 py-1 text-xs font-medium text-white">
    {{ label }}
    <button
      type="button"
      class="ml-0.5 flex h-4 w-4 items-center justify-center rounded-full hover:bg-white/20 focus:outline-none"
      aria-label="Удалить фильтр"
      @click="emit('remove')"
    >
      <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
        <path d="M1 1l6 6M7 1L1 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </button>
  </span>
</template>
