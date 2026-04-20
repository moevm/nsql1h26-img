<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts, dismiss } = useToast()

const iconMap = {
  success: '✓',
  error: '✕',
  info: 'i',
}

const colorMap = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
}
</script>

<template>
  <Teleport to="body">
    <div
      class="pointer-events-none fixed bottom-6 right-6 z-50 flex flex-col gap-3"
      aria-live="polite"
      aria-label="Уведомления"
    >
      <TransitionGroup
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="translate-y-2 opacity-0"
        enter-to-class="translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="translate-y-0 opacity-100"
        leave-to-class="translate-y-2 opacity-0"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="pointer-events-auto flex w-80 items-start gap-3 rounded-xl border px-4 py-3 shadow-lg"
          :class="colorMap[toast.type]"
          role="status"
        >
          <span class="shrink-0 text-sm font-semibold">{{ iconMap[toast.type] }}</span>
          <p class="flex-1 text-sm">{{ toast.message }}</p>
          <button
            class="shrink-0 opacity-60 transition-opacity hover:opacity-100"
            aria-label="Закрыть"
            @click="dismiss(toast.id)"
          >
            ✕
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
