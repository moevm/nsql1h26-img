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
import { registerSchema } from '@/schemas/auth'

const router = useRouter()
const authStore = useAuthStore()

const serverError = ref<string | null>(null)

const { handleSubmit, isSubmitting, setErrors } = useForm({
  validationSchema: toTypedSchema(registerSchema),
})

const { value: username, errorMessage: usernameError } = useField<string>('username')
const { value: email, errorMessage: emailError } = useField<string>('email')
const { value: password, errorMessage: passwordError } = useField<string>('password')
const { value: password2, errorMessage: password2Error } = useField<string>('password2')

const onSubmit = handleSubmit(async (values) => {
  serverError.value = null
  try {
    await authStore.register(values)
    router.push({ name: 'register-success' })
  } catch (err) {
    serverError.value = mapDrfErrors(err, setErrors) ?? 'Ошибка регистрации'
  }
})
</script>

<template>
  <AuthLayout>
    <div class="w-full max-w-sm">
      <div class="mb-8 flex flex-col items-center gap-2 text-center">
        <Logo />
        <p class="mt-2 text-sm text-neutral-500">Создайте аккаунт</p>
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

        <Field label="Имя пользователя" :error="usernameError" required>
          <Input v-model="username" type="text" placeholder="username" autocomplete="username" />
        </Field>

        <Field label="Email" :error="emailError" required>
          <Input v-model="email" type="email" placeholder="you@example.com" autocomplete="email" />
        </Field>

        <Field label="Пароль" :error="passwordError" required>
          <Input
            v-model="password"
            type="password"
            placeholder="••••••••"
            autocomplete="new-password"
          />
        </Field>

        <Field label="Повторите пароль" :error="password2Error" required>
          <Input
            v-model="password2"
            type="password"
            placeholder="••••••••"
            autocomplete="new-password"
          />
        </Field>

        <Button type="submit" :loading="isSubmitting" block>Зарегистрироваться</Button>
      </form>

      <p class="mt-6 text-center text-sm text-neutral-500">
        Уже есть аккаунт?
        <RouterLink to="/login" class="font-medium text-neutral-900 hover:underline">
          Войти
        </RouterLink>
      </p>
    </div>
  </AuthLayout>
</template>
