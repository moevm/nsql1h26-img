<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from '@/components/ui/Button.vue'

const router = useRouter()

function goHome() {
  router.push('/')
}
</script>

<template>
  <section class="flex flex-col items-center justify-center gap-4 py-24 text-center">
    <h1 class="text-5xl font-semibold tracking-tight text-neutral-900 sm:text-6xl">Ошибка 404</h1>
    <p class="max-w-md text-sm text-neutral-500">
      Данный файл скорее всего был удалён и более не доступен.
    </p>
    <Button class="mt-2" variant="primary" @click="goHome">Главная</Button>
  </section>
</template>
