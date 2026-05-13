<script setup lang="ts">
import { ref, reactive, computed, onUnmounted, onMounted, nextTick } from 'vue'
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'
import AppShell from '@/layout/AppShell.vue'
import FilterChip from '@/components/gallery/FilterChip.vue'
import { statsApi } from '@/api/stats'
import type { XAxisField, MetricField } from '@/api/types'

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

// ── Axis / metric config ──────────────────────────────────────────
const X_AXIS_OPTIONS: { value: XAxisField; label: string }[] = [
  { value: 'month', label: 'Месяц' },
  { value: 'day', label: 'День' },
  { value: 'year', label: 'Год' },
  { value: 'image_format', label: 'Формат изображения' },
  { value: 'megapixels', label: 'Размер в Мегапикселях' },
]

const METRIC_OPTIONS: { value: MetricField; label: string; unit: string }[] = [
  { value: 'count', label: 'Количество загрузок', unit: '' },
  { value: 'total_size_mb', label: 'Суммарный объём (МБ)', unit: ' МБ' },
  { value: 'avg_size_mb', label: 'Средний объём (МБ)', unit: ' МБ' },
  { value: 'total_megapixels', label: 'Суммарный размер (МП)', unit: ' МП' },
  { value: 'likes_count', label: 'Количество лайков', unit: '' },
]

const FORMATS = ['PNG', 'JPG', 'JPEG', 'WEBP', 'BMP', 'GIF', 'TIFF']

const COLORS = [
  '#6366f1',
  '#f59e0b',
  '#10b981',
  '#ef4444',
  '#3b82f6',
  '#8b5cf6',
  '#ec4899',
  '#14b8a6',
  '#f97316',
  '#84cc16',
]

// ── State ─────────────────────────────────────────────────────────
const xAxis = ref<XAxisField>('month')
const metric = ref<MetricField>('count')

const filters = reactive({
  search: '',
  author: '',
  date_from: '',
  date_to: '',
  image_format: '',
  min_size_mb: '',
  max_size_mb: '',
  min_width: '',
  max_width: '',
  min_height: '',
  max_height: '',
})

const showMoreFilters = ref(false)

// ── Active chips ──────────────────────────────────────────────────
const activeChips = computed(() => {
  const chips: { key: keyof typeof filters; label: string }[] = []
  if (filters.search) chips.push({ key: 'search', label: `Поиск: ${filters.search}` })
  if (filters.author) chips.push({ key: 'author', label: `Автор: ${filters.author}` })
  if (filters.image_format)
    chips.push({ key: 'image_format', label: `Формат: ${filters.image_format}` })
  if (filters.date_from) chips.push({ key: 'date_from', label: `С ${filters.date_from}` })
  if (filters.date_to) chips.push({ key: 'date_to', label: `По ${filters.date_to}` })
  if (filters.min_size_mb) chips.push({ key: 'min_size_mb', label: `От ${filters.min_size_mb} МБ` })
  if (filters.max_size_mb) chips.push({ key: 'max_size_mb', label: `До ${filters.max_size_mb} МБ` })
  if (filters.min_width) chips.push({ key: 'min_width', label: `Ш ≥ ${filters.min_width}px` })
  if (filters.max_width) chips.push({ key: 'max_width', label: `Ш ≤ ${filters.max_width}px` })
  if (filters.min_height) chips.push({ key: 'min_height', label: `В ≥ ${filters.min_height}px` })
  if (filters.max_height) chips.push({ key: 'max_height', label: `В ≤ ${filters.max_height}px` })
  return chips
})

function removeChip(key: keyof typeof filters) {
  filters[key] = ''
}

function clearAll() {
  for (const k of Object.keys(filters) as (keyof typeof filters)[]) {
    filters[k] = ''
  }
}

function toggleFormat(fmt: string) {
  filters.image_format = filters.image_format === fmt ? '' : fmt
}

// ── Chart ─────────────────────────────────────────────────────────
const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

type LoadState = 'idle' | 'loading' | 'empty' | 'ready' | 'error'
const loadState = ref<LoadState>('idle')
const loadError = ref<string | null>(null)
const chartTitle = ref('')

function destroyChart() {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

const selectedMetric = computed(
  () => METRIC_OPTIONS.find((m) => m.value === metric.value) ?? METRIC_OPTIONS[0],
)

async function buildChart() {
  loadState.value = 'loading'
  loadError.value = null

  const params: Record<string, unknown> = { x_axis: xAxis.value, metric: metric.value }
  for (const [k, v] of Object.entries(filters)) {
    if (v !== '') params[k] = v
  }

  let labels: string[]
  let data: number[]
  let metricLabel: string
  let xLabel: string

  try {
    const resp = await statsApi.get(params as Parameters<typeof statsApi.get>[0])
    ;({ labels, data, metric_label: metricLabel, x_label: xLabel } = resp.data)
  } catch (err) {
    loadError.value = err instanceof Error ? err.message : 'Произошла ошибка'
    loadState.value = 'error'
    return
  }

  if (labels.length === 0) {
    loadState.value = 'empty'
    destroyChart()
    return
  }

  chartTitle.value = `${metricLabel} по параметру «${xLabel}»`
  loadState.value = 'ready'
  await nextTick()

  renderChart(labels, data, metricLabel)
}

function renderChart(labels: string[], data: number[], metricLabel: string) {
  if (!chartCanvas.value) return
  destroyChart()

  const unit = selectedMetric.value.unit

  chartInstance = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: metricLabel,
          data,
          backgroundColor: labels.map((_, i) => COLORS[i % COLORS.length] + 'cc'),
          borderColor: labels.map((_, i) => COLORS[i % COLORS.length]),
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.parsed.y}${unit}`,
          },
        },
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          beginAtZero: true,
          ticks: {
            callback: (val) => `${val}${unit}`,
          },
        },
      },
    },
  })
}

onMounted(() => buildChart())
onUnmounted(() => destroyChart())
</script>

<template>
  <AppShell>
    <div class="flex flex-col gap-8 py-8">
      <h1 class="text-2xl font-semibold text-neutral-900">Статистика</h1>

      <!-- ── Filter section ──────────────────────────────────────── -->
      <section>
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-400">
          Условия поиска
        </h2>

        <!-- Main filter row -->
        <div class="flex flex-wrap items-center gap-2">
          <!-- Search -->
          <input
            v-model="filters.search"
            type="search"
            placeholder="Поиск по названию..."
            class="h-8 w-48 rounded-full border border-neutral-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-400"
          />

          <!-- Format pills -->
          <div class="flex flex-wrap gap-1">
            <button
              v-for="fmt in FORMATS"
              :key="fmt"
              type="button"
              class="rounded-full border px-3 py-0.5 text-xs font-medium transition-colors"
              :class="
                filters.image_format === fmt
                  ? 'border-neutral-900 bg-neutral-900 text-white'
                  : 'border-neutral-200 bg-white text-neutral-700 hover:border-neutral-400'
              "
              @click="toggleFormat(fmt)"
            >
              {{ fmt }}
            </button>
          </div>

          <!-- More filters toggle -->
          <button
            type="button"
            class="flex items-center gap-1 rounded-full border border-neutral-200 bg-white px-3 py-1 text-xs font-medium text-neutral-700 transition-colors hover:border-neutral-400"
            @click="showMoreFilters = !showMoreFilters"
          >
            Ещё фильтры
            <svg
              width="10"
              height="10"
              viewBox="0 0 10 10"
              fill="none"
              class="transition-transform"
              :class="showMoreFilters ? 'rotate-180' : ''"
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
            v-if="activeChips.length > 0"
            type="button"
            class="text-xs text-neutral-500 underline hover:text-neutral-900"
            @click="clearAll"
          >
            Сбросить всё
          </button>
        </div>

        <!-- Expanded filters -->
        <div v-if="showMoreFilters" class="mt-3 rounded-2xl border border-neutral-200 bg-white p-4">
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div class="flex flex-col gap-1.5">
              <span class="text-xs font-medium text-neutral-500">Автор</span>
              <input
                v-model="filters.author"
                type="text"
                placeholder="Имя пользователя..."
                class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
            </div>

            <div class="flex flex-col gap-1.5">
              <span class="text-xs font-medium text-neutral-500">Дата загрузки</span>
              <input
                v-model="filters.date_from"
                type="date"
                class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
              <input
                v-model="filters.date_to"
                type="date"
                class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
            </div>

            <div class="flex flex-col gap-1.5">
              <span class="text-xs font-medium text-neutral-500">Размер файла (МБ)</span>
              <input
                v-model="filters.min_size_mb"
                type="number"
                min="0"
                step="0.1"
                placeholder="От"
                class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
              <input
                v-model="filters.max_size_mb"
                type="number"
                min="0"
                step="0.1"
                placeholder="До"
                class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
            </div>

            <div class="flex flex-col gap-1.5">
              <span class="text-xs font-medium text-neutral-500">Ширина (px)</span>
              <input
                v-model="filters.min_width"
                type="number"
                min="0"
                placeholder="От"
                class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
              <input
                v-model="filters.max_width"
                type="number"
                min="0"
                placeholder="До"
                class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
            </div>

            <div class="flex flex-col gap-1.5">
              <span class="text-xs font-medium text-neutral-500">Высота (px)</span>
              <input
                v-model="filters.min_height"
                type="number"
                min="0"
                placeholder="От"
                class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
              <input
                v-model="filters.max_height"
                type="number"
                min="0"
                placeholder="До"
                class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              />
            </div>
          </div>

          <div class="mt-4 flex justify-end">
            <button
              type="button"
              class="rounded-full bg-neutral-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-neutral-700"
              @click="showMoreFilters = false"
            >
              Готово
            </button>
          </div>
        </div>

        <!-- Active chips -->
        <div v-if="activeChips.length > 0" class="mt-2 flex flex-wrap gap-2">
          <FilterChip
            v-for="chip in activeChips"
            :key="chip.key"
            :label="chip.label"
            @remove="removeChip(chip.key)"
          />
        </div>
      </section>

      <!-- ── Display settings + chart ───────────────────────────── -->
      <section>
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wide text-neutral-400">
          Настройки отображения
        </h2>

        <div class="flex gap-6">
          <!-- Left: X axis radio buttons -->
          <div class="w-52 shrink-0 rounded-2xl border border-neutral-200 bg-white p-4">
            <p class="mb-3 text-xs font-semibold text-neutral-500">Ось X</p>
            <div class="flex flex-col gap-2">
              <label
                v-for="opt in X_AXIS_OPTIONS"
                :key="opt.value"
                class="flex cursor-pointer items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm transition-colors"
                :class="
                  xAxis === opt.value
                    ? 'bg-neutral-900 text-white'
                    : 'text-neutral-700 hover:bg-neutral-50'
                "
              >
                <input type="radio" :value="opt.value" v-model="xAxis" class="sr-only" />
                <span
                  class="flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 transition-colors"
                  :class="
                    xAxis === opt.value
                      ? 'border-white bg-white'
                      : 'border-neutral-400 bg-transparent'
                  "
                >
                  <span v-if="xAxis === opt.value" class="h-2 w-2 rounded-full bg-neutral-900" />
                </span>
                {{ opt.label }}
              </label>
            </div>
          </div>

          <!-- Right: metric + build + chart -->
          <div class="flex min-w-0 flex-1 flex-col gap-4">
            <!-- Controls row -->
            <div class="flex flex-wrap items-center gap-3">
              <select
                v-model="metric"
                class="rounded-full border border-neutral-200 bg-white px-4 py-1.5 text-sm font-medium text-neutral-900 focus:outline-none focus:ring-2 focus:ring-neutral-400"
              >
                <option v-for="opt in METRIC_OPTIONS" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>

              <button
                type="button"
                class="rounded-full bg-emerald-500 px-5 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-emerald-600 disabled:opacity-60"
                :disabled="loadState === 'loading'"
                @click="buildChart"
              >
                {{ loadState === 'loading' ? 'Загрузка...' : 'Построить' }}
              </button>
            </div>

            <!-- Chart area -->
            <div class="rounded-2xl border border-neutral-200 bg-white p-5">
              <p v-if="chartTitle" class="mb-3 text-center text-sm font-medium text-neutral-600">
                {{ chartTitle }}
              </p>

              <div v-if="loadState === 'loading'" class="flex h-64 items-center justify-center">
                <span class="text-sm text-neutral-400">Загрузка...</span>
              </div>
              <div v-else-if="loadState === 'error'" class="flex h-64 items-center justify-center">
                <span class="text-sm text-red-500">{{ loadError }}</span>
              </div>
              <div v-else-if="loadState === 'empty'" class="flex h-64 items-center justify-center">
                <span class="text-sm text-neutral-400">Нет данных для выбранных фильтров</span>
              </div>
              <div v-else class="relative h-72">
                <canvas ref="chartCanvas" />
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </AppShell>
</template>
