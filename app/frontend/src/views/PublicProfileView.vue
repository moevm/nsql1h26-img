<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '@/layout/AppShell.vue'
import Spinner from '@/components/ui/Spinner.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Field from '@/components/ui/Field.vue'
import { authApi } from '@/api/auth'
import type { PublicUser } from '@/api/types'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const authStore = useAuthStore()
const { success, error: toastError } = useToast()

const user = ref<PublicUser | null>(null)
const state = ref<'loading' | 'error' | 'ready'>('loading')

const publishBlocked = ref(false)
const hourlyLimit = ref('5')
const dailyLimit = ref('30')
const isSaving = ref(false)

watch(user, (val) => {
  if (val) {
    publishBlocked.value = val.publish_blocked
    hourlyLimit.value = String(val.hourly_post_limit)
    dailyLimit.value = String(val.daily_post_limit)
  }
}, { immediate: true })

onMounted(async () => {
  try {
    const { data } = await authApi.getPublicProfile(route.params.username as string)
    user.value = data
    state.value = 'ready'
  } catch {
    state.value = 'error'
  }
})

async function savePublishSettings() {
  if (!user.value) return
  isSaving.value = true
  try {
    const { data } = await authApi.updatePublishSettings(user.value.username, {
      publish_blocked: publishBlocked.value,
      hourly_post_limit: parseInt(hourlyLimit.value, 10),
      daily_post_limit: parseInt(dailyLimit.value, 10),
    })
    user.value = data
    success('Настройки публикации сохранены')
  } catch {
    toastError('Ошибка при сохранении настроек')
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <AppShell>
    <div v-if="state === 'loading'" class="flex justify-center py-20">
      <Spinner size="lg" />
    </div>

    <div v-else-if="state === 'error'" class="py-20 text-center">
      <p class="text-xl font-semibold text-neutral-900">Пользователь не найден</p>
    </div>

    <div v-else-if="user" class="mx-auto max-w-md py-12">
      <h1 class="mb-8 text-2xl font-semibold text-neutral-900">Профиль пользователя</h1>

      <div class="rounded-2xl border border-neutral-200 bg-white p-8 shadow-card">
        <div class="mb-6 flex flex-col items-center gap-3">
          <div class="grid h-20 w-20 place-items-center rounded-full bg-neutral-100">
            <svg
              width="36"
              height="36"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="text-neutral-400"
              aria-hidden="true"
            >
              <circle cx="12" cy="8" r="4" />
              <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" />
            </svg>
          </div>
          <p class="text-lg font-semibold text-neutral-900">{{ user.username }}</p>
        </div>

        <dl class="flex flex-col gap-3 text-sm">
          <div v-if="user.first_name || user.last_name" class="flex justify-between">
            <dt class="text-neutral-500">Имя</dt>
            <dd class="font-medium text-neutral-900">
              {{ [user.first_name, user.last_name].filter(Boolean).join(' ') }}
            </dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-neutral-500">Дата регистрации</dt>
            <dd class="font-medium text-neutral-900">
              {{ new Date(user.date_joined).toLocaleDateString('ru-RU') }}
            </dd>
          </div>
        </dl>

        <div
          v-if="authStore.isAdmin && user.role !== 'admin'"
          class="mt-6 border-t border-neutral-200 pt-6"
        >
          <h2 class="mb-4 text-sm font-semibold text-neutral-700">Управление публикациями</h2>
          <div class="flex flex-col gap-4">
            <label class="flex cursor-pointer items-center gap-3 text-sm">
              <input
                v-model="publishBlocked"
                type="checkbox"
                class="h-4 w-4 rounded border-neutral-300 accent-red-500"
              />
              <span class="text-neutral-700">Заблокировать публикации</span>
            </label>
            <Field label="Лимит в час">
              <Input v-model="hourlyLimit" type="number" :min="1" />
            </Field>
            <Field label="Лимит в сутки">
              <Input v-model="dailyLimit" type="number" :min="1" />
            </Field>
            <div class="flex justify-end">
              <Button type="button" :loading="isSaving" @click="savePublishSettings">
                Сохранить
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
