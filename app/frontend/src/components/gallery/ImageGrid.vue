<script setup lang="ts">
import type { Image } from '@/api/types'
import ImageCard from '@/components/gallery/ImageCard.vue'

defineProps<{ images: Image[] }>()
</script>

<template>
  <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
    <ImageCard v-for="image in images" :key="image.id" :image="image" />
  </div>
</template>
