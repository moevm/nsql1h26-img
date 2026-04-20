<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  page: number
  count: number
  pageSize?: number
}>()

const emit = defineEmits<{ change: [page: number] }>()

const size = computed(() => props.pageSize ?? 10)
const totalPages = computed(() => Math.ceil(props.count / size.value))

const pages = computed(() => {
  const total = totalPages.value
  const cur = props.page
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const result: (number | '…')[] = [1]
  if (cur > 3) result.push('…')
  for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) result.push(i)
  if (cur < total - 2) result.push('…')
  result.push(total)
  return result
})
</script>

<template>
  <nav
    v-if="totalPages > 1"
    class="flex items-center justify-center gap-1"
    aria-label="Пагинация"
  >
    <button
      class="rounded-lg px-3 py-1.5 text-sm text-neutral-600 transition-colors hover:bg-neutral-100 disabled:opacity-40"
      :disabled="page <= 1"
      @click="emit('change', page - 1)"
    >
      вернуться
    </button>

    <template v-for="p in pages" :key="p">
      <span v-if="p === '…'" class="px-1 text-sm text-neutral-400">…</span>
      <button
        v-else
        class="min-w-[2rem] rounded-lg px-2 py-1.5 text-sm transition-colors"
        :class="
          p === page
            ? 'bg-neutral-900 font-medium text-white'
            : 'text-neutral-600 hover:bg-neutral-100'
        "
        :aria-current="p === page ? 'page' : undefined"
        @click="emit('change', p)"
      >
        {{ p }}
      </button>
    </template>

    <button
      class="rounded-lg px-3 py-1.5 text-sm text-neutral-600 transition-colors hover:bg-neutral-100 disabled:opacity-40"
      :disabled="page >= totalPages"
      @click="emit('change', page + 1)"
    >
      дальше
    </button>
  </nav>
</template>
