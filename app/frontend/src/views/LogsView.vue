<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppShell from '@/layout/AppShell.vue'
import Spinner from '@/components/ui/Spinner.vue'
import Pagination from '@/components/ui/Pagination.vue'
import { logsApi } from '@/api/logs'
import type { ActionTypeOption, Log } from '@/api/types'

const logs = ref<Log[]>([])
const count = ref(0)
const loading = ref(false)
const error = ref<string | null>(null)

const page = ref(1)
const PAGE_SIZE = 20

const filterAction = ref('')
const filterUsername = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')

const actionTypes = ref<ActionTypeOption[]>([])

const expandedId = ref<string | null>(null)

async function fetchLogs() {
  loading.value = true
  error.value = null
  try {
    const { data } = await logsApi.list({
      page: page.value,
      action: filterAction.value || undefined,
      username: filterUsername.value || undefined,
      date_from: filterDateFrom.value || undefined,
      date_to: filterDateTo.value || undefined,
    })
    logs.value = data.results
    count.value = data.count
  } catch {
    error.value = 'Не удалось загрузить логи'
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  page.value = 1
  fetchLogs()
}

function resetFilters() {
  filterAction.value = ''
  filterUsername.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
  page.value = 1
  fetchLogs()
}

function onPageChange(p: number) {
  page.value = p
  fetchLogs()
}

function toggleExpand(id: string) {
  expandedId.value = expandedId.value === id ? null : id
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const ACTION_COLORS: Record<string, string> = {
  image_uploaded: 'bg-emerald-100 text-emerald-700',
  image_deleted: 'bg-red-100 text-red-700',
  metadata_updated: 'bg-blue-100 text-blue-700',
  user_registered: 'bg-violet-100 text-violet-700',
  user_logged_in: 'bg-sky-100 text-sky-700',
  user_logged_out: 'bg-neutral-100 text-neutral-600',
  password_changed: 'bg-orange-100 text-orange-700',
  password_recovered: 'bg-orange-100 text-orange-700',
  search_executed: 'bg-yellow-100 text-yellow-700',
  stats_viewed: 'bg-teal-100 text-teal-700',
  database_exported: 'bg-indigo-100 text-indigo-700',
  database_imported: 'bg-indigo-100 text-indigo-700',
  profile_updated: 'bg-pink-100 text-pink-700',
  email_changed: 'bg-pink-100 text-pink-700',
  admin_user_restrictions_updated: 'bg-red-100 text-red-700',
  image_liked: 'bg-rose-100 text-rose-700',
  image_unliked: 'bg-neutral-100 text-neutral-600',
}

function actionColor(action: string) {
  return ACTION_COLORS[action] ?? 'bg-neutral-100 text-neutral-600'
}

onMounted(async () => {
  const [, types] = await Promise.all([
    fetchLogs(),
    logsApi.actionTypes().then((r) => r.data),
  ])
  actionTypes.value = types
})
</script>

<template>
  <AppShell>
    <div class="flex flex-col gap-6 py-8">
      <h1 class="text-2xl font-semibold text-neutral-900">Журнал действий</h1>

      <!-- Filters -->
      <div class="rounded-2xl border border-neutral-200 bg-white p-5">
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div class="flex flex-col gap-1.5">
            <span class="text-xs font-medium text-neutral-500">Тип действия</span>
            <select
              v-model="filterAction"
              class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            >
              <option value="">Все</option>
              <option v-for="t in actionTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>

          <div class="flex flex-col gap-1.5">
            <span class="text-xs font-medium text-neutral-500">Пользователь</span>
            <input
              v-model="filterUsername"
              type="text"
              placeholder="Имя пользователя..."
              class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
              @keydown.enter="applyFilters"
            />
          </div>

          <div class="flex flex-col gap-1.5">
            <span class="text-xs font-medium text-neutral-500">С даты</span>
            <input
              v-model="filterDateFrom"
              type="date"
              class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            />
          </div>

          <div class="flex flex-col gap-1.5">
            <span class="text-xs font-medium text-neutral-500">По дату</span>
            <input
              v-model="filterDateTo"
              type="date"
              class="rounded-lg border border-neutral-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900"
            />
          </div>
        </div>

        <div class="mt-4 flex items-center justify-end gap-3">
          <button
            type="button"
            class="text-sm text-neutral-500 underline hover:text-neutral-900"
            @click="resetFilters"
          >
            Сбросить
          </button>
          <button
            type="button"
            class="rounded-full bg-neutral-900 px-5 py-1.5 text-sm font-medium text-white hover:bg-neutral-700"
            @click="applyFilters"
          >
            Применить
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="rounded-2xl border border-neutral-200 bg-white shadow-card">
        <div v-if="loading" class="flex items-center justify-center py-20">
          <Spinner size="lg" />
        </div>

        <div v-else-if="error" class="py-16 text-center text-sm text-red-500">{{ error }}</div>

        <div v-else-if="logs.length === 0" class="py-16 text-center text-sm text-neutral-400">
          Записи не найдены
        </div>

        <template v-else>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-neutral-100 text-left text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  <th class="px-5 py-3.5">Дата</th>
                  <th class="px-5 py-3.5">Пользователь</th>
                  <th class="px-5 py-3.5">Действие</th>
                  <th class="px-5 py-3.5">Детали</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-neutral-100">
                <template v-for="log in logs" :key="log.id">
                  <tr class="transition-colors hover:bg-neutral-50">
                    <td class="whitespace-nowrap px-5 py-3.5 font-mono text-xs text-neutral-500">
                      {{ formatDate(log.created_at) }}
                    </td>
                    <td class="px-5 py-3.5 font-medium text-neutral-800">
                      {{ log.username ?? '—' }}
                    </td>
                    <td class="px-5 py-3.5">
                      <span
                        class="inline-block rounded-full px-2.5 py-0.5 text-xs font-medium"
                        :class="actionColor(log.action)"
                      >
                        {{ log.action_display }}
                      </span>
                    </td>
                    <td class="px-5 py-3.5">
                      <button
                        v-if="Object.keys(log.payload).length > 0"
                        type="button"
                        class="text-xs text-neutral-400 underline underline-offset-2 hover:text-neutral-700"
                        @click="toggleExpand(log.id)"
                      >
                        {{ expandedId === log.id ? 'Скрыть' : 'Показать' }}
                      </button>
                      <span v-else class="text-xs text-neutral-300">—</span>
                    </td>
                  </tr>
                  <tr v-if="expandedId === log.id" :key="log.id + '-payload'">
                    <td colspan="4" class="bg-neutral-50 px-5 py-3">
                      <pre class="overflow-x-auto rounded-lg bg-neutral-100 px-3 py-2 text-xs text-neutral-700">{{ JSON.stringify(log.payload, null, 2) }}</pre>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>

          <div class="flex items-center justify-between border-t border-neutral-100 px-5 py-3.5">
            <span class="text-xs text-neutral-400">Всего записей: {{ count }}</span>
            <Pagination :page="page" :count="count" :page-size="PAGE_SIZE" @change="onPageChange" />
          </div>
        </template>
      </div>
    </div>
  </AppShell>
</template>
