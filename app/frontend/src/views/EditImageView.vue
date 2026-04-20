<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import AppShell from '@/layout/AppShell.vue'
import Button from '@/components/ui/Button.vue'
import Field from '@/components/ui/Field.vue'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Spinner from '@/components/ui/Spinner.vue'
import { imagesApi } from '@/api/images'
import { mapDrfErrors } from '@/api/axios'
import { editSchema } from '@/schemas/image'
import { useToast } from '@/composables/useToast'
import type { Image } from '@/api/types'

const route = useRoute()
const router = useRouter()
const { success, error: toastError } = useToast()

const image = ref<Image | null>(null)
const loadState = ref<'loading' | 'error' | 'ready'>('loading')
const serverError = ref<string | null>(null)

const { handleSubmit, isSubmitting, setErrors, setValues } = useForm({
  validationSchema: toTypedSchema(editSchema),
})

const { value: title, errorMessage: titleError } = useField<string>('title')
const { value: description, errorMessage: descriptionError } = useField<string>('description')

onMounted(async () => {
  try {
    const { data } = await imagesApi.retrieve(route.params.id as string)
    image.value = data
    setValues({ title: data.title, description: data.description ?? '' })
    loadState.value = 'ready'
  } catch {
    loadState.value = 'error'
  }
})

const onSubmit = handleSubmit(async (values) => {
  if (!image.value) return
  serverError.value = null

  const patch: Record<string, string> = {}
  if (values.title !== image.value.title) patch.title = values.title
  if ((values.description ?? '') !== (image.value.description ?? ''))
    patch.description = values.description ?? ''

  if (!Object.keys(patch).length) {
    router.push({ name: 'image-detail', params: { id: image.value.id } })
    return
  }

  try {
    await imagesApi.patch(image.value.id, patch)
    success('Публикация обновлена')
    router.push({ name: 'image-detail', params: { id: image.value.id } })
  } catch (err) {
    serverError.value = mapDrfErrors(err, setErrors) ?? 'Ошибка при сохранении'
    toastError(serverError.value)
  }
})
</script>

<template>
  <AppShell>
    <div v-if="loadState === 'loading'" class="flex justify-center py-20">
      <Spinner size="lg" />
    </div>

    <div v-else-if="loadState === 'error'" class="py-20 text-center text-sm text-neutral-500">
      Не удалось загрузить публикацию
    </div>

    <div v-else class="mx-auto max-w-xl py-8">
      <h1 class="mb-8 text-2xl font-semibold text-neutral-900">Редактирование публикации</h1>

      <div v-if="image" class="mb-6 overflow-hidden rounded-2xl border border-neutral-200 bg-neutral-100">
        <img :src="image.file" :alt="image.title" class="max-h-48 w-full object-contain" />
      </div>

      <form class="flex flex-col gap-6" @submit.prevent="onSubmit">
        <p
          v-if="serverError"
          role="alert"
          class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"
        >
          {{ serverError }}
        </p>

        <Field label="Название" :error="titleError" required>
          <Input v-model="title" placeholder="Введите название" />
        </Field>

        <Field label="Описание" :error="descriptionError">
          <Textarea v-model="description" placeholder="Необязательное описание..." />
        </Field>

        <div class="flex justify-end gap-3">
          <Button
            variant="secondary"
            type="button"
            @click="router.push({ name: 'image-detail', params: { id: route.params.id } })"
          >
            Отмена
          </Button>
          <Button type="submit" :loading="isSubmitting">Сохранить</Button>
        </div>
      </form>
    </div>
  </AppShell>
</template>
