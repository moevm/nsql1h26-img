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
const likePending = ref(false)

const canEdit = computed(
  () =>
    authStore.isAuthenticated &&
    image.value &&
    (authStore.user?.id === image.value.author || authStore.isAdmin),
)

async function toggleLike() {
  if (!image.value || !authStore.isAuthenticated) return
  likePending.value = true
  try {
    const { data } = await imagesApi.like(image.value.id)
    image.value.is_liked = data.liked
    image.value.likes_count = data.likes_count
  } catch {
    toastError('Не удалось обновить лайк')
  } finally {
    likePending.value = false
  }
}

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
      <RouterLink to="/" class="text-sm font-medium text-neutral-900 underline"
        >На главную</RouterLink
      >
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
          <Button variant="secondary" size="sm" @click="showDeleteModal = true"> Удалить </Button>
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
              <dd class="font-medium text-neutral-900">
                <RouterLink
                  :to="{ name: 'public-profile', params: { username: image.author_username } }"
                  class="text-blue-600 hover:text-blue-800 hover:underline"
                  >{{ image.author_username }}</RouterLink
                >
              </dd>
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

          <div class="flex items-center gap-3 pt-2">
            <button
              v-if="authStore.isAuthenticated"
              :disabled="likePending"
              class="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition-colors disabled:opacity-50"
              :class="
                image.is_liked
                  ? 'bg-red-50 text-red-500 hover:bg-red-100'
                  : 'bg-neutral-100 text-neutral-500 hover:bg-neutral-200 hover:text-neutral-700'
              "
              @click="toggleLike"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                :fill="image.is_liked ? 'currentColor' : 'none'"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                />
              </svg>
              {{ image.likes_count }}
            </button>
            <span v-else class="flex items-center gap-1.5 text-sm text-neutral-400">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                />
              </svg>
              {{ image.likes_count }}
            </span>
          </div>
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
          <Button class="!bg-red-600 hover:!bg-red-700" :loading="deleting" @click="confirmDelete">
            Удалить
          </Button>
        </div>
      </div>
    </Modal>
  </AppShell>
</template>
