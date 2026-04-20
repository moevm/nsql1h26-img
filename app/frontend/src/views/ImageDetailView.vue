<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import AppShell from '@/layout/AppShell.vue'
import Spinner from '@/components/ui/Spinner.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'
import { imagesApi } from '@/api/images'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import type { Image } from '@/api/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { success, error: toastError } = useToast()

const image = ref<Image | null>(null)
const state = ref<'loading' | 'error' | 'ready'>('loading')
const showDeleteModal = ref(false)
const deleting = ref(false)

const canEdit = computed(
  () =>
    authStore.isAuthenticated &&
    image.value &&
    (authStore.user?.id === image.value.author || authStore.isAdmin),
)

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatSize(mb: number) {
  if (mb < 1) return `${(mb * 1024).toFixed(0)} КБ`
  return `${mb.toFixed(2)} МБ`
}

async function confirmDelete() {
  if (!image.value) return
  deleting.value = true
  try {
    await imagesApi.remove(image.value.id)
    success('Публикация удалена')
    router.push({ name: 'gallery' })
  } catch {
    toastError('Не удалось удалить публикацию')
    deleting.value = false
    showDeleteModal.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await imagesApi.retrieve(route.params.id as string)
    image.value = data
    state.value = 'ready'
  } catch {
    state.value = 'error'
  }
})
</script>

<template>
  <AppShell>
    <div v-if="state === 'loading'" class="flex justify-center py-20">
      <Spinner size="lg" />
    </div>

    <div v-else-if="state === 'error'" class="flex flex-col items-center gap-3 py-20 text-center">
      <p class="text-xl font-semibold text-neutral-900">Ошибка 404</p>
      <p class="text-sm text-neutral-500">
        Данный файл скорее всего был удалён и более не доступен.
      </p>
      <RouterLink to="/" class="text-sm font-medium text-neutral-900 underline">На главную</RouterLink>
    </div>

    <div v-else-if="image" class="mx-auto max-w-4xl">
      <div class="mb-6 flex items-center justify-between">
        <RouterLink to="/" class="text-sm text-neutral-500 hover:text-neutral-900">
          ← Назад к галерее
        </RouterLink>
        <div v-if="canEdit" class="flex gap-2">
          <RouterLink :to="{ name: 'edit-image', params: { id: image.id } }">
            <Button variant="secondary" size="sm">Редактировать</Button>
          </RouterLink>
          <Button variant="secondary" size="sm" @click="showDeleteModal = true">
            Удалить
          </Button>
        </div>
      </div>

      <div class="grid gap-8 lg:grid-cols-[1fr_300px]">
        <div class="overflow-hidden rounded-2xl border border-neutral-200 bg-neutral-100">
          <img :src="image.file" :alt="image.title" class="h-full w-full object-contain" />
        </div>

        <div class="flex flex-col gap-6">
          <div>
            <h1 class="text-xl font-semibold text-neutral-900">{{ image.title }}</h1>
            <p v-if="image.description" class="mt-2 text-sm text-neutral-600">
              {{ image.description }}
            </p>
          </div>

          <dl class="flex flex-col gap-3 text-sm">
            <div class="flex justify-between border-b border-neutral-100 pb-3">
              <dt class="text-neutral-500">Автор</dt>
              <dd class="font-medium text-neutral-900">{{ image.author_username }}</dd>
            </div>
            <div class="flex justify-between border-b border-neutral-100 pb-3">
              <dt class="text-neutral-500">Формат</dt>
              <dd class="font-medium text-neutral-900">{{ image.image_format }}</dd>
            </div>
            <div class="flex justify-between border-b border-neutral-100 pb-3">
              <dt class="text-neutral-500">Размер</dt>
              <dd class="font-medium text-neutral-900">
                {{ image.width }} × {{ image.height }} px
              </dd>
            </div>
            <div class="flex justify-between border-b border-neutral-100 pb-3">
              <dt class="text-neutral-500">Вес</dt>
              <dd class="font-medium text-neutral-900">{{ formatSize(image.file_size_mb) }}</dd>
            </div>
            <div class="flex justify-between border-b border-neutral-100 pb-3">
              <dt class="text-neutral-500">Загружено</dt>
              <dd class="font-medium text-neutral-900">{{ formatDate(image.created_at) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-neutral-500">Обновлено</dt>
              <dd class="font-medium text-neutral-900">{{ formatDate(image.updated_at) }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>

    <Modal :open="showDeleteModal" title="Удаление публикации" @close="showDeleteModal = false">
      <div class="flex flex-col gap-5">
        <div>
          <h2 class="text-lg font-semibold text-neutral-900">Удалить публикацию?</h2>
          <p class="mt-1 text-sm text-neutral-500">
            «{{ image?.title }}» будет удалена безвозвратно.
          </p>
        </div>
        <div class="flex justify-end gap-3">
          <Button variant="secondary" :disabled="deleting" @click="showDeleteModal = false">
            Отмена
          </Button>
          <Button
            class="!bg-red-600 hover:!bg-red-700"
            :loading="deleting"
            @click="confirmDelete"
          >
            Удалить
          </Button>
        </div>
      </div>
    </Modal>
  </AppShell>
</template>
