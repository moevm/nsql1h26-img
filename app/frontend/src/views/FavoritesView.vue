<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppShell from '@/layout/AppShell.vue'
import ImageGrid from '@/components/gallery/ImageGrid.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { RouterLink } from 'vue-router'
import { imagesApi } from '@/api/images'
import type { Image } from '@/api/types'

const images = ref<Image[]>([])
const state = ref<'loading' | 'error' | 'empty' | 'ready'>('loading')

async function load() {
  state.value = 'loading'
  try {
    const allResults: Image[] = []
    let page = 1
    while (true) {
      const { data } = await imagesApi.list({ liked_by_me: true, page })
      allResults.push(...data.results)
      if (!data.next) break
      page++
    }
    images.value = allResults
    state.value = allResults.length === 0 ? 'empty' : 'ready'
  } catch {
    state.value = 'error'
  }
}

onMounted(() => load())
</script>

<template>
  <AppShell>
    <div class="flex flex-col gap-6">
      <h1 class="text-2xl font-semibold text-neutral-900">Избранное</h1>

      <div v-if="state === 'loading'" class="flex justify-center py-20">
        <Spinner size="lg" />
      </div>

      <EmptyState
        v-else-if="state === 'empty'"
        title="Избранное пусто"
        description="Ставьте лайки на изображения, чтобы они появились здесь"
      >
        <RouterLink to="/" class="text-sm font-medium text-neutral-900 underline">
          Перейти в галерею
        </RouterLink>
      </EmptyState>

      <div v-else-if="state === 'error'" class="flex flex-col items-center gap-3 py-20 text-center">
        <p class="text-sm text-neutral-500">Не удалось загрузить избранное</p>
        <button class="text-sm font-medium text-neutral-900 underline" @click="load()">
          Повторить
        </button>
      </div>

      <ImageGrid v-else :images="images" />
    </div>
  </AppShell>
</template>
