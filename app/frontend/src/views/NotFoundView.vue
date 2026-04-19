<script setup lang="ts">
import { RouterLink } from 'vue-router'
import AppShell from '@/layout/AppShell.vue'
import Button from '@/components/ui/Button.vue'
</script>

<template>
  <AppShell>
    <section class="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <h1 class="text-5xl font-semibold tracking-tight text-neutral-900 sm:text-6xl">Ошибка 404</h1>
      <p class="max-w-md text-sm text-neutral-500">
        Данный файл скорее всего был удалён и более не доступен.
      </p>
      <RouterLink to="/">
        <Button class="mt-2">Главная</Button>
      </RouterLink>
    </section>
  </AppShell>
</template>
