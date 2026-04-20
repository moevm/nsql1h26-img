<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps<{
  open: boolean
  title?: string
}>()

const emit = defineEmits<{ close: [] }>()

const panelRef = ref<HTMLElement | null>(null)
let previouslyFocused: HTMLElement | null = null

function getFocusable() {
  return Array.from(
    panelRef.value?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    ) ?? [],
  ).filter((el) => !el.hasAttribute('disabled'))
}

function onKeydown(e: KeyboardEvent) {
  if (!props.open) return
  if (e.key === 'Escape') { emit('close'); return }
  if (e.key !== 'Tab') return

  const focusable = getFocusable()
  if (!focusable.length) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]

  if (e.shiftKey && document.activeElement === first) {
    last.focus(); e.preventDefault()
  } else if (!e.shiftKey && document.activeElement === last) {
    first.focus(); e.preventDefault()
  }
}

watch(
  () => props.open,
  (val) => {
    if (val) {
      previouslyFocused = document.activeElement as HTMLElement
      document.body.style.overflow = 'hidden'
      setTimeout(() => getFocusable()[0]?.focus(), 30)
    } else {
      document.body.style.overflow = ''
      previouslyFocused?.focus()
    }
  },
)

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
      >
        <div class="absolute inset-0 bg-black/50" aria-hidden="true" @click="emit('close')" />

        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="scale-95 opacity-0"
          enter-to-class="scale-100 opacity-100"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="scale-100 opacity-100"
          leave-to-class="scale-95 opacity-0"
        >
          <div
            v-if="open"
            ref="panelRef"
            class="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-xl"
          >
            <slot />
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
