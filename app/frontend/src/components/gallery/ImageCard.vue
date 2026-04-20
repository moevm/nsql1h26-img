<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { Image } from '@/api/types'

defineProps<{ image: Image }>()

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

function formatSize(mb: number) {
  if (mb < 1) return `${(mb * 1024).toFixed(0)} КБ`
  return `${mb.toFixed(1)} МБ`
}
</script>

<template>
  <RouterLink
    :to="{ name: 'image-detail', params: { id: image.id } }"
    class="group flex flex-col overflow-hidden rounded-2xl border border-neutral-200 bg-white shadow-card transition-shadow hover:shadow-md"
  >
    <div class="aspect-[4/3] overflow-hidden bg-neutral-100">
      <img
        :src="image.file"
        :alt="image.title"
        class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        loading="lazy"
        @error="($event.target as HTMLImageElement).style.opacity = '0'"
      />
    </div>

    <div class="flex flex-col gap-1 p-3">
      <p class="truncate text-sm font-medium text-neutral-900">{{ image.title }}</p>
      <div class="flex items-center justify-between text-xs text-neutral-500">
        <span>{{ formatDate(image.created_at) }}</span>
        <span>{{ formatSize(image.file_size_mb) }}</span>
      </div>
    </div>
  </RouterLink>
</template>
