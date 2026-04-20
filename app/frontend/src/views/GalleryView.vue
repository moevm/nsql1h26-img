<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import AppShell from '@/layout/AppShell.vue'
import ImageGrid from '@/components/gallery/ImageGrid.vue'
import Pagination from '@/components/ui/Pagination.vue'
import Spinner from '@/components/ui/Spinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import Input from '@/components/ui/Input.vue'
import { imagesApi } from '@/api/images'
import { useFilterQuery } from '@/composables/useFilterQuery'
import type { Image } from '@/api/types'
import { useDebounceFn } from '@vueuse/core'

const { page, search, setPage, setSearch, toApiParams } = useFilterQuery()

const images = ref<Image[]>([])
const count = ref(0)
const state = ref<'loading' | 'error' | 'empty' | 'ready'>('loading')
const searchInput = ref(search.value)

async function load() {
  state.value = 'loading'
  try {
    const { data } = await imagesApi.list(toApiParams())
    images.value = data.results
    count.value = data.count
    state.value = data.results.length === 0 ? 'empty' : 'ready'
  } catch {
    state.value = 'error'
  }
}

const debouncedSearch = useDebounceFn((val: string) => {
  setSearch(val)
}, 300)

watch(() => searchInput.value, debouncedSearch)
watch([page, search], load)
onMounted(load)
</script>

<template>
  <AppShell>
    <div class="flex flex-col gap-6">
      <div class="flex items-center gap-3">
        <Input
          v-model="searchInput"
          type="search"
          placeholder="Поиск по названию..."
          class="max-w-sm"
        />
      </div>

      <div v-if="state === 'loading'" class="flex justify-center py-20">
        <Spinner size="lg" />
      </div>

      <EmptyState
        v-else-if="state === 'empty'"
        title="Изображений пока нет"
        :description="search ? 'Попробуйте изменить запрос' : 'Загрузите первое изображение'"
      />

      <div v-else-if="state === 'error'" class="flex flex-col items-center gap-3 py-20 text-center">
        <p class="text-sm text-neutral-500">Не удалось загрузить изображения</p>
        <button class="text-sm font-medium text-neutral-900 underline" @click="load">
          Повторить
        </button>
      </div>

      <template v-else>
        <ImageGrid :images="images" />
        <Pagination :page="page" :count="count" @change="setPage" />
      </template>
    </div>
  </AppShell>
</template>
