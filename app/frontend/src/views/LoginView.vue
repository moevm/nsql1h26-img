<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import AuthLayout from '@/layout/AuthLayout.vue'
import Logo from '@/layout/Logo.vue'
import Button from '@/components/ui/Button.vue'
import Field from '@/components/ui/Field.vue'
import Input from '@/components/ui/Input.vue'
import { useAuthStore } from '@/stores/auth'
import { mapDrfErrors } from '@/api/axios'
import { loginSchema } from '@/schemas/auth'

const router = useRouter()
const authStore = useAuthStore()

const serverError = ref<string | null>(null)

const { handleSubmit, isSubmitting, setErrors } = useForm({
  validationSchema: toTypedSchema(loginSchema),
})

const { value: login, errorMessage: loginError } = useField<string>('login')
const { value: password, errorMessage: passwordError } = useField<string>('password')

const onSubmit = handleSubmit(async (values) => {
  serverError.value = null
  try {
    await authStore.login(values)
    const next = (router.currentRoute.value.query.next as string) || '/'
    router.push(next)
  } catch (err) {
    serverError.value = mapDrfErrors(err, setErrors) ?? 'Неверный логин или пароль'
  }
})
</script>

<template>
  <AuthLayout>
    <div class="w-full max-w-sm">
      <div class="mb-8 flex flex-col items-center gap-2 text-center">
        <Logo />
        <p class="mt-2 text-sm text-neutral-500">Войдите в аккаунт</p>
      </div>

      <form
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

        <Field label="Логин или email" :error="loginError" required>
          <Input
            v-model="login"
            type="text"
            placeholder="username или email"
            autocomplete="username"
          />
        </Field>

        <Field label="Пароль" :error="passwordError" required>
          <Input
            v-model="password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
          />
        </Field>

        <Button type="submit" :loading="isSubmitting" block>Войти</Button>
      </form>

      <p class="mt-6 text-center text-sm text-neutral-500">
        Нет аккаунта?
        <RouterLink to="/register" class="font-medium text-neutral-900 hover:underline">
          Зарегистрироваться
        </RouterLink>
      </p>
    </div>
  </AuthLayout>
</template>
