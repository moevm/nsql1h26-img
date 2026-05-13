<script setup lang="ts">
import { ref } from 'vue'
import AppShell from '@/layout/AppShell.vue'
import Button from '@/components/ui/Button.vue'
import { exportBackup, importBackup } from '@/api/system'
import { useToast } from '@/composables/useToast'

const toast = useToast()

const exporting = ref(false)

async function handleExport() {
  exporting.value = true
  try {
    const { blob, filename } = await exportBackup()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.error('Ошибка при экспорте. Попробуйте ещё раз.')
  } finally {
    exporting.value = false
  }
}

const importFile = ref<File | null>(null)
const importing = ref(false)
const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

function openFilePicker() {
  fileInputRef.value?.click()
}

function onFileSelected(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) importFile.value = file
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  isDragging.value = true
}

function onDragLeave() {
  isDragging.value = false
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) importFile.value = file
}

async function handleImport() {
  if (!importFile.value) return
  importing.value = true
  try {
    const res = await importBackup(importFile.value)
    toast.success(res.detail ?? 'Импорт выполнен успешно.')
    importFile.value = null
    if (fileInputRef.value) fileInputRef.value.value = ''
  } catch (err: unknown) {
    const msg =
      (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
      'Ошибка при импорте. Проверьте файл и попробуйте ещё раз.'
    toast.error(msg)
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <AppShell>
    <div class="mx-auto max-w-5xl px-6 py-10">
      <h1 class="mb-8 text-2xl font-bold text-neutral-900">Резервное копирование</h1>

      <div class="grid grid-cols-2 gap-6">
        <!-- Export panel -->
        <div class="flex flex-col rounded-2xl border border-neutral-200 bg-white p-8 shadow-card">
          <h2 class="mb-3 text-center text-lg font-semibold text-neutral-900">Экспорт системы</h2>
          <p class="mb-8 text-center text-sm leading-relaxed text-neutral-500">
            Скачать полную копию базы данных изображений в формате ZIP-архива.
          </p>
          <div class="mt-auto flex justify-center">
            <Button :loading="exporting" @click="handleExport">
              Скачать файл
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
            </Button>
          </div>
        </div>

        <!-- Import panel -->
        <div class="flex flex-col rounded-2xl bg-neutral-900 p-8">
          <h2 class="mb-3 text-center text-lg font-semibold text-white">Импорт системы</h2>
          <p class="mb-6 text-center text-sm leading-relaxed text-neutral-400">
            Загрузка файла полностью заменит текущую базу данных. Все несохранённые изменения будут
            потеряны.
          </p>

          <p class="mb-2 text-sm font-medium text-neutral-300">Загрузить файл</p>

          <!-- Drop zone -->
          <div
            class="mb-4 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed py-12 transition-colors"
            :class="
              isDragging ? 'border-neutral-400 bg-neutral-700' : 'border-neutral-600 bg-neutral-800'
            "
            @click="openFilePicker"
            @dragover="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="mb-2 text-neutral-400"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="12" y1="18" x2="12" y2="12" />
              <line x1="9" y1="15" x2="15" y2="15" />
            </svg>
            <span class="text-sm text-neutral-500">Click to upload</span>
          </div>

          <p class="mb-3 text-xs font-medium uppercase tracking-wider text-neutral-500">ZIP</p>

          <!-- Selected file indicator -->
          <div
            v-if="importFile"
            class="mb-4 flex items-center justify-between rounded-xl bg-neutral-800 px-4 py-3"
          >
            <div class="min-w-0">
              <p class="truncate text-sm font-medium text-white">{{ importFile.name }}</p>
              <p class="text-xs text-neutral-400">Файл выбран</p>
            </div>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="ml-3 shrink-0 text-green-400"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>

          <div class="mt-auto flex justify-center">
            <Button
              variant="secondary"
              :loading="importing"
              :disabled="!importFile"
              @click="handleImport"
            >
              Импортировать
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Hidden file input -->
    <input ref="fileInputRef" type="file" accept=".zip" class="hidden" @change="onFileSelected" />
  </AppShell>
</template>
