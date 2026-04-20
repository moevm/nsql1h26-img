<script setup lang="ts">
defineProps<{ size?: 'sm' | 'md' | 'lg' }>()

const sizeMap = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
}
</script>

<template>
  <span
    :class="[
      'block animate-spin rounded-full border-2 border-neutral-200 border-t-neutral-700',
      sizeMap[size ?? 'md'],
    ]"
    role="status"
    aria-label="Загрузка"
  />
</template>
