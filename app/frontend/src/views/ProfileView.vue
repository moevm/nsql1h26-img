<script setup lang="ts">
import { ref } from 'vue'
import AppShell from '@/layout/AppShell.vue'
import Button from '@/components/ui/Button.vue'
import Field from '@/components/ui/Field.vue'
import Input from '@/components/ui/Input.vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { authApi } from '@/api/auth'
import { mapDrfErrors } from '@/api/axios'
import { changePasswordSchema } from '@/schemas/auth'

const authStore = useAuthStore()
const router = useRouter()
const { success } = useToast()

async function handleLogout() {
  await authStore.logout()
  success('Вы вышли из аккаунта')
  router.push({ name: 'login' })
}

const showPasswordForm = ref(false)
const serverError = ref<string | null>(null)

const { handleSubmit, isSubmitting, setErrors, resetForm } = useForm({
  validationSchema: toTypedSchema(changePasswordSchema),
})

const { value: oldPassword, errorMessage: oldPasswordError } = useField<string>('old_password')
const { value: newPassword, errorMessage: newPasswordError } = useField<string>('new_password')
const { value: newPassword2, errorMessage: newPassword2Error } = useField<string>('new_password2')

const onChangePassword = handleSubmit(async (values) => {
  serverError.value = null
  try {
    const { data } = await authApi.changePassword(values)
    authStore.token = data.token
    success('Пароль успешно изменён')
    showPasswordForm.value = false
    resetForm()
  } catch (err) {
    const nonField = mapDrfErrors(err, setErrors)
    if (nonField) serverError.value = nonField
  }
})

function togglePasswordForm() {
  showPasswordForm.value = !showPasswordForm.value
  if (!showPasswordForm.value) {
    resetForm()
    serverError.value = null
  }
}
</script>

<template>
  <AppShell>
    <div class="mx-auto max-w-md py-12">
      <h1 class="mb-8 text-2xl font-semibold text-neutral-900">Профиль</h1>

      <div class="rounded-2xl border border-neutral-200 bg-white p-8 shadow-card">
        <div class="mb-6 flex flex-col items-center gap-3">
          <div class="grid h-20 w-20 place-items-center rounded-full bg-neutral-100">
            <svg
              width="36"
              height="36"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="text-neutral-400"
              aria-hidden="true"
            >
              <circle cx="12" cy="8" r="4" />
              <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" />
            </svg>
          </div>
          <p class="text-lg font-semibold text-neutral-900">{{ authStore.user?.username }}</p>
        </div>

        <dl class="flex flex-col gap-3 text-sm">
          <div class="flex justify-between">
            <dt class="text-neutral-500">Email</dt>
            <dd class="font-medium text-neutral-900">{{ authStore.user?.email }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-neutral-500">Роль</dt>
            <dd class="font-medium text-neutral-900">{{ authStore.user?.role }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-neutral-500">Дата регистрации</dt>
            <dd class="font-medium text-neutral-900">
              {{
                authStore.user?.date_joined
                  ? new Date(authStore.user.date_joined).toLocaleDateString('ru-RU')
                  : '—'
              }}
            </dd>
          </div>
        </dl>

        <div class="mt-8 flex flex-col gap-3">
          <Button variant="secondary" block @click="togglePasswordForm">
            {{ showPasswordForm ? 'Отмена' : 'Изменить пароль' }}
          </Button>
          <Button variant="secondary" block @click="handleLogout">Выйти из аккаунта</Button>
        </div>
      </div>

      <div
        v-if="showPasswordForm"
        class="mt-4 rounded-2xl border border-neutral-200 bg-white p-8 shadow-card"
      >
        <h2 class="mb-5 text-base font-semibold text-neutral-900">Изменить пароль</h2>

        <form class="flex flex-col gap-4" @submit.prevent="onChangePassword">
          <p
            v-if="serverError"
            role="alert"
            class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"
          >
            {{ serverError }}
          </p>

          <Field label="Текущий пароль" :error="oldPasswordError" required>
            <Input
              v-model="oldPassword"
              type="password"
              placeholder="••••••••"
              autocomplete="current-password"
            />
          </Field>

          <Field label="Новый пароль" :error="newPasswordError" required>
            <Input
              v-model="newPassword"
              type="password"
              placeholder="••••••••"
              autocomplete="new-password"
            />
          </Field>

          <Field label="Повторите новый пароль" :error="newPassword2Error" required>
            <Input
              v-model="newPassword2"
              type="password"
              placeholder="••••••••"
              autocomplete="new-password"
            />
          </Field>

          <Button type="submit" :loading="isSubmitting" block>Сохранить</Button>
        </form>
      </div>
    </div>
  </AppShell>
</template>
