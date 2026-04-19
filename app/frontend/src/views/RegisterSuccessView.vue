<script setup lang="ts">
import { RouterLink } from 'vue-router'
import AuthLayout from '@/layout/AuthLayout.vue'
import Logo from '@/layout/Logo.vue'
import Button from '@/components/ui/Button.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <AuthLayout>
    <div class="w-full max-w-sm text-center">
      <Logo class="mx-auto mb-8" />

      <div
        class="flex flex-col items-center gap-6 rounded-2xl border border-neutral-200 bg-white p-10 shadow-card"
      >
        <div class="grid h-16 w-16 place-items-center rounded-full bg-green-50">
          <svg
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="text-green-600"
            aria-hidden="true"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>

        <div>
          <h1 class="text-xl font-semibold text-neutral-900">Аккаунт зарегистрирован успешно!</h1>
          <p v-if="authStore.user" class="mt-1 text-sm text-neutral-500">
            Добро пожаловать, {{ authStore.user.username }}
          </p>
        </div>

        <RouterLink to="/">
          <Button>Начать</Button>
        </RouterLink>
      </div>
    </div>
  </AuthLayout>
</template>
