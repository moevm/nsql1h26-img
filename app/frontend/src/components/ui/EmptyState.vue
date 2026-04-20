<script setup lang="ts">
defineProps<{
  title?: string
  description?: string
}>()
</script>

<template>
  <div class="flex flex-col items-center gap-4 py-20 text-center">
    <div class="grid h-16 w-16 place-items-center rounded-full bg-neutral-100">
      <svg
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="text-neutral-400"
        aria-hidden="true"
      >
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="m3 9 4-4 4 4 4-4 4 4" />
        <path d="M3 15h18" />
      </svg>
    </div>
    <div>
      <p class="font-medium text-neutral-900">{{ title ?? 'Ничего не найдено' }}</p>
      <p v-if="description" class="mt-1 text-sm text-neutral-500">{{ description }}</p>
    </div>
    <slot />
  </div>
</template>
