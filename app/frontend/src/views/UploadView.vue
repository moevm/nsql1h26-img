<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'
import AppShell from '@/layout/AppShell.vue'
import Button from '@/components/ui/Button.vue'
import Field from '@/components/ui/Field.vue'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import UploadDropzone from '@/components/gallery/UploadDropzone.vue'
import { imagesApi } from '@/api/images'
import { mapDrfErrors } from '@/api/axios'
import { useToast } from '@/composables/useToast'

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp', 'image/gif']
const MAX_SIZE_BYTES = 15 * 1024 * 1024

const formSchema = z.object({
  title: z.string().min(1, 'Введите название').max(255, 'Максимум 255 символов'),
  description: z.string().max(1000, 'Максимум 1000 символов').optional(),
})

const router = useRouter()
const { success, error: toastError } = useToast()

const serverError = ref<string | null>(null)
const selectedFile = ref<File | null>(null)
const fileError = ref<string | null>(null)

const { handleSubmit, isSubmitting, setErrors } = useForm({
  validationSchema: toTypedSchema(formSchema),
})

const { value: title, errorMessage: titleError } = useField<string>('title')
const { value: description, errorMessage: descriptionError } = useField<string>('description')

function onFileChange(file: File | null) {
  selectedFile.value = file
  fileError.value = null
}

function validateFile(): boolean {
  if (!selectedFile.value) {
    fileError.value = 'Выберите файл'
    return false
  }
  if (!ALLOWED_TYPES.includes(selectedFile.value.type)) {
    fileError.value = 'Допустимы только JPEG, PNG, WEBP, BMP, GIF'
    return false
  }
  if (selectedFile.value.size > MAX_SIZE_BYTES) {
    fileError.value = 'Файл не должен превышать 15 МБ'
    return false
  }
  return true
}

const onSubmit = handleSubmit(async (values) => {
  if (!validateFile()) return

  serverError.value = null
  const form = new FormData()
  form.append('file', selectedFile.value!)
  form.append('title', values.title)
  if (values.description) form.append('description', values.description)

  try {
    const { data } = await imagesApi.create(form)
    success('Изображение загружено')
    router.push({ name: 'image-detail', params: { id: data.id } })
  } catch (err) {
    const axiosErr = err as import('axios').AxiosError<{ detail?: string }>
    const httpStatus = axiosErr?.response?.status
    const detail = axiosErr?.response?.data?.detail

    if (httpStatus === 403) {
      serverError.value = detail ?? 'Возможность публикаций была ограничена.'
    } else if (httpStatus === 429) {
      serverError.value = detail ?? 'Превышен лимит публикаций. Попробуйте позже.'
    } else {
      serverError.value = mapDrfErrors(err, setErrors) ?? 'Ошибка при загрузке'
    }
    toastError(serverError.value)
  }
})
</script>

<template>
  <AppShell>
    <div class="mx-auto max-w-xl py-8">
      <h1 class="mb-8 text-2xl font-semibold text-neutral-900">Создание публикации</h1>

      <form class="flex flex-col gap-6" @submit.prevent="onSubmit">
        <p
          v-if="serverError"
          role="alert"
          class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"
        >
          {{ serverError }}
        </p>

        <div>
          <p class="mb-2 text-sm font-medium text-neutral-700">
            Изображение <span class="text-red-500" aria-hidden="true">*</span>
          </p>
          <UploadDropzone
            :model-value="selectedFile"
            :error="fileError ?? undefined"
            @update:model-value="onFileChange"
          />
        </div>

        <Field label="Название" :error="titleError" required>
          <Input v-model="title" placeholder="Введите название" />
        </Field>

        <Field label="Описание" :error="descriptionError">
          <Textarea v-model="description" placeholder="Необязательное описание..." />
        </Field>

        <div class="flex justify-end gap-3">
          <Button variant="secondary" type="button" @click="router.back()">Отмена</Button>
          <Button type="submit" :loading="isSubmitting">Опубликовать</Button>
        </div>
      </form>
    </div>
  </AppShell>
</template>
