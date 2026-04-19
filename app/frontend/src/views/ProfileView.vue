<script setup lang="ts">
import AppShell from '@/layout/AppShell.vue'
import Button from '@/components/ui/Button.vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'

const authStore = useAuthStore()
const router = useRouter()
const { success } = useToast()

async function handleLogout() {
  await authStore.logout()
  success('Вы вышли из аккаунта')
  router.push({ name: 'login' })
}
</script>

<template>
  <AppShell>
    <div class="mx-auto max-w-md py-12">
      <h1 class="mb-8 text-2xl font-semibold text-neutral-900">Профиль</h1>

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
          <p class="text-lg font-semibold text-neutral-900">{{ authStore.user?.username }}</p>
        </div>

        <dl class="flex flex-col gap-3 text-sm">
          <div class="flex justify-between">
            <dt class="text-neutral-500">Email</dt>
            <dd class="font-medium text-neutral-900">{{ authStore.user?.email }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-neutral-500">Роль</dt>
            <dd class="font-medium text-neutral-900">{{ authStore.user?.role }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-neutral-500">Дата регистрации</dt>
            <dd class="font-medium text-neutral-900">
              {{
                authStore.user?.date_joined
                  ? new Date(authStore.user.date_joined).toLocaleDateString('ru-RU')
                  : '—'
              }}
            </dd>
          </div>
        </dl>

        <div class="mt-8">
          <Button variant="secondary" block @click="handleLogout">Выйти из аккаунта</Button>
        </div>
      </div>
    </div>
  </AppShell>
</template>
