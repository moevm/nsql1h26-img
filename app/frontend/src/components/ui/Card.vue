<script setup lang="ts">
interface Props {
  as?: keyof HTMLElementTagNameMap
  padded?: boolean
}

const { as = 'div', padded = false } = defineProps<Props>()
</script>

<template>
  <component
    :is="as"
    class="overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-card"
    :class="padded ? 'p-6' : ''"
  >
    <slot />
  </component>
</template>
