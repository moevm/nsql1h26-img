<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { useFilterQuery } from '@/composables/useFilterQuery'
import FilterChip from './FilterChip.vue'
import Input from '@/components/ui/Input.vue'

const {
  search,
  author,
  dateFrom,
  dateTo,
  imageFormat,
  minSizeMb,
  maxSizeMb,
  minWidth,
  maxWidth,
  minHeight,
  maxHeight,
  setSearch,
  update,
  clearAll,
} = useFilterQuery()

const FORMATS = ['PNG', 'JPG', 'JPEG', 'WEBP', 'BMP', 'GIF', 'TIFF']

const searchInput = ref(search.value)
const showMore = ref(false)

const localAuthor = ref(author.value)
const localDateFrom = ref(dateFrom.value)
const localDateTo = ref(dateTo.value)
const localMinSize = ref(minSizeMb.value)
const localMaxSize = ref(maxSizeMb.value)
const localMinWidth = ref(minWidth.value)
const localMaxWidth = ref(maxWidth.value)
const localMinHeight = ref(minHeight.value)
const localMaxHeight = ref(maxHeight.value)

const debouncedSearch = useDebounceFn((val: string) => setSearch(val), 300)
watch(searchInput, debouncedSearch)

watch(
  [author, dateFrom, dateTo, minSizeMb, maxSizeMb, minWidth, maxWidth, minHeight, maxHeight],
  () => {
    localAuthor.value = author.value
    localDateFrom.value = dateFrom.value
    localDateTo.value = dateTo.value
    localMinSize.value = minSizeMb.value
    localMaxSize.value = maxSizeMb.value
    localMinWidth.value = minWidth.value
    localMaxWidth.value = maxWidth.value
    localMinHeight.value = minHeight.value
    localMaxHeight.value = maxHeight.value
  },
)

function toggleFormat(fmt: string) {
  update({ image_format: imageFormat.value === fmt ? undefined : fmt, page: undefined })
}

function applyMore() {
  update({
    author: localAuthor.value || undefined,
    date_from: localDateFrom.value || undefined,
    date_to: localDateTo.value || undefined,
    min_size_mb: localMinSize.value || undefined,
    max_size_mb: localMaxSize.value || undefined,
    min_width: localMinWidth.value || undefined,
    max_width: localMaxWidth.value || undefined,
    min_height: localMinHeight.value || undefined,
    max_height: localMaxHeight.value || undefined,
    page: undefined,
  })
  showMore.value = false
}

function clearMore() {
  localAuthor.value = ''
  localDateFrom.value = ''
  localDateTo.value = ''
  localMinSize.value = ''
  localMaxSize.value = ''
  localMinWidth.value = ''
  localMaxWidth.value = ''
  localMinHeight.value = ''
  localMaxHeight.value = ''
  applyMore()
}

const activeChips = computed(() => {
  const chips: { key: string; label: string }[] = []
  if (author.value) chips.push({ key: 'author', label: `Автор: ${author.value}` })
  if (imageFormat.value) chips.push({ key: 'image_format', label: `Формат: ${imageFormat.value}` })
  if (dateFrom.value) chips.push({ key: 'date_from', label: `С ${dateFrom.value}` })
  if (dateTo.value) chips.push({ key: 'date_to', label: `По ${dateTo.value}` })
  if (minSizeMb.value) chips.push({ key: 'min_size_mb', label: `От ${minSizeMb.value} МБ` })
  if (maxSizeMb.value) chips.push({ key: 'max_size_mb', label: `До ${maxSizeMb.value} МБ` })
  if (minWidth.value) chips.push({ key: 'min_width', label: `Ш ≥ ${minWidth.value}px` })
  if (maxWidth.value) chips.push({ key: 'max_width', label: `Ш ≤ ${maxWidth.value}px` })
  if (minHeight.value) chips.push({ key: 'min_height', label: `В ≥ ${minHeight.value}px` })
  if (maxHeight.value) chips.push({ key: 'max_height', label: `В ≤ ${maxHeight.value}px` })
  return chips
})

const hasFilters = computed(() => activeChips.value.length > 0 || !!search.value)

function removeChip(key: string) {
  update({ [key]: undefined, page: undefined })
}

function handleClearAll() {
  searchInput.value = ''
  searchInput.value = ''
  clearAll()
  showMore.value = false
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <!-- Main row: search + format pills + more filters -->
    <div class="flex flex-wrap items-center gap-2">
      <Input
        v-model="searchInput"
        type="search"
        placeholder="Поиск по названию..."
        class="w-56 flex-shrink-0"
      />

      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="fmt in FORMATS"
          :key="fmt"
          type="button"
          class="rounded-full border px-3 py-1 text-xs font-medium transition-colors"
          :class="
            imageFormat === fmt
              ? 'border-neutral-900 bg-neutral-900 text-white'
              : 'border-neutral-200 bg-white text-neutral-700 hover:border-neutral-400'
          "
          @click="toggleFormat(fmt)"
        >
          {{ fmt }}
        </button>
      </div>

      <button
        type="button"
        class="flex items-center gap-1 rounded-full border border-neutral-200 bg-white px-3 py-1 text-xs font-medium text-neutral-700 transition-colors hover:border-neutral-400"
        @click="showMore = !showMore"
      >
        Ещё фильтры
        <svg
          width="10"
          height="10"
          viewBox="0 0 10 10"
          fill="none"
          class="transition-transform"
          :class="showMore ? 'rotate-180' : ''"
        >
          <path
            d="M2 3.5l3 3 3-3"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>

      <button
        v-if="hasFilters"
        type="button"
        class="text-xs text-neutral-500 underline hover:text-neutral-900"
        @click="handleClearAll"
      >
        Сбросить всё
      </button>
    </div>

    <!-- Expanded filters panel -->
    <div v-if="showMore" class="rounded-2xl border border-neutral-200 bg-white p-4">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <!-- Author -->
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-neutral-500">Автор</span>
          <input
            v-model="localAuthor"
            type="text"
            class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="Имя пользователя..."
          />
        </div>

        <!-- Date range -->
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-neutral-500">Дата загрузки</span>
          <input
            v-model="localDateFrom"
            type="date"
            class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="С"
          />
          <input
            v-model="localDateTo"
            type="date"
            class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="По"
          />
        </div>

        <!-- File size -->
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-neutral-500">Размер файла (МБ)</span>
          <input
            v-model="localMinSize"
            type="number"
            min="0"
            step="0.1"
            class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="От"
          />
          <input
            v-model="localMaxSize"
            type="number"
            min="0"
            step="0.1"
            class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="До"
          />
        </div>

        <!-- Width -->
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-neutral-500">Ширина (px)</span>
          <input
            v-model="localMinWidth"
            type="number"
            min="0"
            class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="От"
          />
          <input
            v-model="localMaxWidth"
            type="number"
            min="0"
            class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="До"
          />
        </div>

        <!-- Height -->
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-neutral-500">Высота (px)</span>
          <input
            v-model="localMinHeight"
            type="number"
            min="0"
            class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="От"
          />
          <input
            v-model="localMaxHeight"
            type="number"
            min="0"
            class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            placeholder="До"
          />
        </div>
      </div>

      <div class="mt-4 flex justify-end gap-2">
        <button
          type="button"
          class="rounded-full border border-neutral-200 px-4 py-1.5 text-sm font-medium text-neutral-700 hover:border-neutral-400"
          @click="clearMore"
        >
          Очистить
        </button>
        <button
          type="button"
          class="rounded-full bg-neutral-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-neutral-700"
          @click="applyMore"
        >
          Применить
        </button>
      </div>
    </div>

    <!-- Active filter chips -->
    <div v-if="activeChips.length > 0" class="flex flex-wrap gap-2">
      <FilterChip
        v-for="chip in activeChips"
        :key="chip.key"
        :label="chip.label"
        @remove="removeChip(chip.key)"
      />
    </div>
  </div>
</template>
