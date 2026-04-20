<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ modelValue: File | null; error?: string }>()
const emit = defineEmits<{ 'update:modelValue': [File | null] }>()

const isDragging = ref(false)
const previewUrl = ref<string | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

function handleFile(file: File) {
  emit('update:modelValue', file)
  previewUrl.value = URL.createObjectURL(file)
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) handleFile(file)
}

function onInput(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) handleFile(file)
}

function clear() {
  emit('update:modelValue', null)
  previewUrl.value = null
  if (inputRef.value) inputRef.value.value = ''
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <div
      class="relative flex min-h-48 cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed transition-colors"
      :class="[
        isDragging ? 'border-neutral-900 bg-neutral-50' : 'border-neutral-300 bg-white hover:border-neutral-400',
        error ? 'border-red-300' : '',
      ]"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="onDrop"
      @click="inputRef?.click()"
    >
      <template v-if="previewUrl">
        <img
          :src="previewUrl"
          alt="Предпросмотр"
          class="max-h-56 rounded-xl object-contain"
        />
        <p class="text-xs text-neutral-500">{{ props.modelValue?.name }}</p>
        <button
          type="button"
          class="absolute right-3 top-3 grid h-7 w-7 place-items-center rounded-full bg-white shadow hover:bg-neutral-100"
          aria-label="Удалить файл"
          @click.stop="clear"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </template>

      <template v-else>
        <div class="grid h-12 w-12 place-items-center rounded-full bg-neutral-100">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="text-neutral-500" aria-hidden="true">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>
        <div class="text-center">
          <p class="text-sm font-medium text-neutral-900">Перетащите файл или нажмите для выбора</p>
          <p class="mt-1 text-xs text-neutral-500">JPEG, PNG, WEBP, BMP — до 15 МБ</p>
        </div>
      </template>
    </div>

    <p v-if="error" role="alert" class="text-xs text-red-500">{{ error }}</p>

    <input
      ref="inputRef"
      type="file"
      accept="image/jpeg,image/png,image/webp,image/bmp"
      class="hidden"
      @change="onInput"
    />
  </div>
</template>
