<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppShell from '@/layout/AppShell.vue'
import ImageGrid from '@/components/gallery/ImageGrid.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import Button from '@/components/ui/Button.vue'
import { RouterLink } from 'vue-router'
import { imagesApi } from '@/api/images'
import { useAuthStore } from '@/stores/auth'
import type { Image } from '@/api/types'

const authStore = useAuthStore()

const images = ref<Image[]>([])
const count = ref(0)
const page = ref(1)
const state = ref<'loading' | 'error' | 'empty' | 'ready'>('loading')

async function load(p = 1) {
  state.value = 'loading'
  page.value = p
  try {
    // TODO: switch to backend ?author= filter once available
    const allResults: Image[] = []
    let currentPage = 1
    while (true) {
      const { data } = await imagesApi.list({ page: currentPage })
      const userImages = data.results.filter(
        (img) => img.author_username === authStore.user?.username,
      )
      allResults.push(...userImages)
      if (!data.next || allResults.length >= 50) break
      currentPage++
    }

    images.value = allResults
    count.value = allResults.length
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
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-semibold text-neutral-900">Мои записи</h1>
        <RouterLink to="/upload">
          <Button size="sm">Загрузить</Button>
        </RouterLink>
      </div>

      <div v-if="state === 'loading'" class="flex justify-center py-20">
        <Spinner size="lg" />
      </div>

      <EmptyState
        v-else-if="state === 'empty'"
        title="У вас пока нет публикаций"
        description="Загрузите первое изображение"
      >
        <RouterLink to="/upload">
          <Button size="sm">Загрузить</Button>
        </RouterLink>
      </EmptyState>

      <div v-else-if="state === 'error'" class="flex flex-col items-center gap-3 py-20 text-center">
        <p class="text-sm text-neutral-500">Не удалось загрузить публикации</p>
        <button class="text-sm font-medium text-neutral-900 underline" @click="load()">
          Повторить
        </button>
      </div>

      <ImageGrid v-else :images="images" />
    </div>
  </AppShell>
</template>
