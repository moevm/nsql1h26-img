<script setup lang="ts">
import { computed } from 'vue'

type Variant = 'primary' | 'secondary' | 'ghost'
type Size = 'sm' | 'md' | 'lg'

interface Props {
  variant?: Variant
  size?: Size
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  loading?: boolean
  block?: boolean
}

const {
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled = false,
  loading = false,
  block = false,
} = defineProps<Props>()

defineEmits<{
  click: [event: MouseEvent]
}>()

const base =
  'inline-flex items-center justify-center gap-2 rounded-full font-medium transition-colors duration-150 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neutral-900/20 focus-visible:ring-offset-2 focus-visible:ring-offset-canvas disabled:cursor-not-allowed disabled:opacity-50'

const sizeMap: Record<Size, string> = {
  sm: 'px-4 py-1.5 text-sm',
  md: 'px-6 py-2.5 text-sm',
  lg: 'px-7 py-3 text-base',
}

const variantMap: Record<Variant, string> = {
  primary: 'bg-neutral-900 text-white hover:bg-neutral-800',
  secondary: 'border border-neutral-200 bg-white text-neutral-900 hover:border-neutral-400',
  ghost: 'bg-transparent text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900',
}

const classes = computed(() => [base, sizeMap[size], variantMap[variant], block ? 'w-full' : ''])
</script>

<template>
  <button
    :type="type"
    :class="classes"
    :disabled="disabled || loading"
    :aria-busy="loading || undefined"
    @click="$emit('click', $event)"
  >
    <span
      v-if="loading"
      class="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-r-transparent"
      aria-hidden="true"
    />
    <slot />
  </button>
</template>
