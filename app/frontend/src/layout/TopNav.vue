<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Logo from '@/layout/Logo.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const publicItems = [{ label: 'Поиск', to: '/' }]

const authItems = [
  { label: 'Избранное', to: '/favorites' },
  { label: 'Создание', to: '/upload' },
  { label: 'Мои записи', to: '/my' },
]
</script>

<template>
  <header class="sticky top-0 z-20 border-b border-neutral-200 bg-canvas/80 backdrop-blur">
    <nav
      class="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-6"
      aria-label="Основная навигация"
    >
      <Logo />

      <div class="flex items-center gap-8">
        <ul class="flex items-center gap-6">
          <li v-for="item in [...publicItems, ...(authStore.isAuthenticated ? authItems : [])]" :key="item.label">
            <RouterLink
              :to="item.to"
              class="group relative text-sm text-neutral-600 transition-colors hover:text-neutral-900"
              active-class="is-active"
            >
              <span>{{ item.label }}</span>
              <span
                class="absolute -bottom-1 left-0 h-px w-full origin-left scale-x-0 bg-neutral-900 transition-transform duration-200 ease-out group-hover:scale-x-100"
                aria-hidden="true"
              />
            </RouterLink>
          </li>
        </ul>

        <RouterLink
          :to="authStore.isAuthenticated ? '/profile' : '/login'"
          :aria-label="authStore.isAuthenticated ? 'Профиль' : 'Войти'"
          :class="[
            'grid h-9 w-9 place-items-center rounded-full border transition-colors',
            authStore.isAuthenticated
              ? 'border-neutral-900 bg-neutral-900 text-white hover:bg-neutral-800 hover:border-neutral-800'
              : 'border-neutral-200 bg-white text-neutral-700 hover:border-neutral-400 hover:text-neutral-900',
          ]"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" />
          </svg>
        </RouterLink>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.is-active {
  @apply font-medium text-neutral-900;
}
.is-active > span:last-child {
  @apply scale-x-100;
}
</style>
