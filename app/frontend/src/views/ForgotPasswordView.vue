<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import AuthLayout from '@/layout/AuthLayout.vue'
import Logo from '@/layout/Logo.vue'
import Button from '@/components/ui/Button.vue'
import Field from '@/components/ui/Field.vue'
import Input from '@/components/ui/Input.vue'
import { authApi } from '@/api/auth'
import { forgotPasswordSchema } from '@/schemas/auth'

const sent = ref(false)
const serverError = ref<string | null>(null)

const { handleSubmit, isSubmitting } = useForm({
  validationSchema: toTypedSchema(forgotPasswordSchema),
})

const { value: email, errorMessage: emailError } = useField<string>('email')

const onSubmit = handleSubmit(async (values) => {
  serverError.value = null
  try {
    await authApi.requestPasswordReset(values)
  } catch {
    // always show success to avoid email enumeration
  }
  sent.value = true
})
</script>

<template>
  <AuthLayout>
    <div class="w-full max-w-sm">
      <div class="mb-8 flex flex-col items-center gap-2 text-center">
        <Logo />
        <p class="mt-2 text-sm text-neutral-500">Восстановление пароля</p>
      </div>

      <div
        v-if="sent"
        class="flex flex-col gap-5 rounded-2xl border border-neutral-200 bg-white p-8 shadow-card"
      >
        <p class="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">
          Если такой email зарегистрирован, письмо с инструкцией отправлено.
        </p>
        <RouterLink
          to="/login"
          class="text-center text-sm font-medium text-neutral-900 hover:underline"
        >
          Вернуться к входу
        </RouterLink>
      </div>

      <form
        v-else
        class="flex flex-col gap-5 rounded-2xl border border-neutral-200 bg-white p-8 shadow-card"
        @submit.prevent="onSubmit"
      >
        <p
          v-if="serverError"
          role="alert"
          class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"
        >
          {{ serverError }}
        </p>

        <Field label="Email" :error="emailError" required>
          <Input v-model="email" type="email" placeholder="you@example.com" autocomplete="email" />
        </Field>

        <Button type="submit" :loading="isSubmitting" block>Отправить ссылку</Button>
      </form>

      <p class="mt-6 text-center text-sm text-neutral-500">
        <RouterLink to="/login" class="font-medium text-neutral-900 hover:underline">
          Вернуться к входу
        </RouterLink>
      </p>
    </div>
  </AuthLayout>
</template>
