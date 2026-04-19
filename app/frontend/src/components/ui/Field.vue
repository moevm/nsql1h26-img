<script setup lang="ts">
defineProps<{
  label: string
  error?: string
  required?: boolean
}>()
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label class="text-sm font-medium text-neutral-700">
      {{ label }}
      <span v-if="required" class="text-red-500" aria-hidden="true">*</span>
    </label>
    <slot />
    <p v-if="error" role="alert" class="text-xs text-red-500">{{ error }}</p>
  </div>
</template>
