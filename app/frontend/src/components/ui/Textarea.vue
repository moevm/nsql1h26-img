<script setup lang="ts">
defineProps<{
  placeholder?: string
  disabled?: boolean
  rows?: number
}>()

const model = defineModel<string>({ default: '' })
</script>

<template>
  <textarea
    v-model="model"
    :placeholder="placeholder"
    :disabled="disabled"
    :rows="rows ?? 4"
    class="w-full resize-none rounded-xl border border-neutral-200 bg-white px-3.5 py-2.5 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-neutral-400 focus:outline-none focus:ring-2 focus:ring-neutral-900/10 disabled:cursor-not-allowed disabled:bg-neutral-50"
  />
</template>
