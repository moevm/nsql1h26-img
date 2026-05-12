<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppShell from '@/layout/AppShell.vue'
import Button from '@/components/ui/Button.vue'
import Field from '@/components/ui/Field.vue'
import Input from '@/components/ui/Input.vue'
import Modal from '@/components/ui/Modal.vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { authApi } from '@/api/auth'
import { mapDrfErrors } from '@/api/axios'
import {
  changePasswordSchema,
  updateProfileSchema,
  changeEmailSchema,
  emailCodeSchema,
} from '@/schemas/auth'

const authStore = useAuthStore()
const router = useRouter()
const { success } = useToast()

async function handleLogout() {
  await authStore.logout()
  success('Вы вышли из аккаунта')
  router.push({ name: 'login' })
}

// ── Edit profile modal ───────────────────────────────────────────
const showProfileModal = ref(false)
const profileServerError = ref<string | null>(null)

const {
  handleSubmit: handleProfileSubmit,
  isSubmitting: isProfileSubmitting,
  setErrors: setProfileErrors,
  resetForm: resetProfileForm,
} = useForm({
  validationSchema: toTypedSchema(updateProfileSchema),
  initialValues: {
    username: authStore.user?.username ?? '',
    first_name: authStore.user?.first_name ?? '',
    last_name: authStore.user?.last_name ?? '',
  },
})

const { value: profileUsername, errorMessage: profileUsernameError } = useField<string>('username')
const { value: firstName, errorMessage: firstNameError } = useField<string>('first_name')
const { value: lastName, errorMessage: lastNameError } = useField<string>('last_name')

const onUpdateProfile = handleProfileSubmit(async (values) => {
  profileServerError.value = null
  try {
    const { data } = await authApi.updateProfile(values)
    authStore.user = data
    success('Профиль обновлён')
    closeProfileModal()
  } catch (err) {
    const nonField = mapDrfErrors(err, setProfileErrors)
    if (nonField) profileServerError.value = nonField
  }
})

function openProfileModal() {
  resetProfileForm({
    values: {
      username: authStore.user?.username ?? '',
      first_name: authStore.user?.first_name ?? '',
      last_name: authStore.user?.last_name ?? '',
    },
  })
  profileServerError.value = null
  showProfileModal.value = true
}

function closeProfileModal() {
  showProfileModal.value = false
  profileServerError.value = null
}

// ── Change email modal (2-step) ──────────────────────────────────
const showEmailModal = ref(false)
const emailStep = ref<1 | 2>(1)

// Step 1 — enter new email
const emailServerError = ref<string | null>(null)

const {
  handleSubmit: handleEmailSubmit,
  isSubmitting: isEmailSubmitting,
  setErrors: setEmailErrors,
  resetForm: resetEmailForm,
} = useForm({
  validationSchema: toTypedSchema(changeEmailSchema),
})

const { value: newEmail, errorMessage: newEmailError } = useField<string>('email')

const onSubmitNewEmail = handleEmailSubmit(async (values) => {
  emailServerError.value = null
  try {
    const { data } = await authApi.updateProfile({ email: values.email })
    authStore.user = data
    if (data.pending_email) {
      emailStep.value = 2
      resetCodeForm()
    } else {
      success('Email обновлён')
      closeEmailModal()
    }
  } catch (err) {
    const nonField = mapDrfErrors(err, setEmailErrors)
    if (nonField) emailServerError.value = nonField
  }
})

// Step 2 — enter confirmation code
const codeServerError = ref<string | null>(null)
const isResending = ref(false)

const {
  handleSubmit: handleCodeSubmit,
  isSubmitting: isCodeSubmitting,
  setErrors: setCodeErrors,
  resetForm: resetCodeForm,
} = useForm({
  validationSchema: toTypedSchema(emailCodeSchema),
})

const { value: codeValue, errorMessage: codeError } = useField<string>('code')

const onConfirmCode = handleCodeSubmit(async (values) => {
  codeServerError.value = null
  try {
    const { data } = await authApi.confirmEmailChange({ code: values.code })
    authStore.user = data
    success('Email успешно изменён')
    closeEmailModal()
  } catch (err) {
    const nonField = mapDrfErrors(err, setCodeErrors)
    if (nonField) codeServerError.value = nonField
  }
})

async function resendCode() {
  if (!authStore.user?.pending_email) return
  isResending.value = true
  try {
    const { data } = await authApi.updateProfile({ email: authStore.user.pending_email })
    authStore.user = data
    success('Код отправлен повторно')
  } catch {
    // ignore
  } finally {
    isResending.value = false
  }
}

function openEmailModal(startAtStep: 1 | 2 = 1) {
  emailStep.value = startAtStep
  emailServerError.value = null
  codeServerError.value = null
  resetEmailForm()
  resetCodeForm()
  showEmailModal.value = true
}

function closeEmailModal() {
  showEmailModal.value = false
  emailServerError.value = null
  codeServerError.value = null
}

// ── Change password modal ────────────────────────────────────────
const showPasswordModal = ref(false)
const passwordServerError = ref<string | null>(null)

const {
  handleSubmit: handlePasswordSubmit,
  isSubmitting: isPasswordSubmitting,
  setErrors: setPasswordErrors,
  resetForm: resetPasswordForm,
} = useForm({
  validationSchema: toTypedSchema(changePasswordSchema),
})

const { value: oldPassword, errorMessage: oldPasswordError } = useField<string>('old_password')
const { value: newPassword, errorMessage: newPasswordError } = useField<string>('new_password')
const { value: newPassword2, errorMessage: newPassword2Error } = useField<string>('new_password2')

const onChangePassword = handlePasswordSubmit(async (values) => {
  passwordServerError.value = null
  try {
    const { data } = await authApi.changePassword(values)
    authStore.token = data.token
    success('Пароль успешно изменён')
    closePasswordModal()
  } catch (err) {
    const nonField = mapDrfErrors(err, setPasswordErrors)
    if (nonField) passwordServerError.value = nonField
  }
})

function openPasswordModal() {
  resetPasswordForm()
  passwordServerError.value = null
  showPasswordModal.value = true
}

function closePasswordModal() {
  showPasswordModal.value = false
  passwordServerError.value = null
  resetPasswordForm()
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
            <dt class="text-neutral-500">Имя</dt>
            <dd class="font-medium text-neutral-900">{{ authStore.user?.first_name || '—' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-neutral-500">Фамилия</dt>
            <dd class="font-medium text-neutral-900">{{ authStore.user?.last_name || '—' }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-neutral-500">Email</dt>
            <dd class="font-medium text-neutral-900">{{ authStore.user?.email }}</dd>
          </div>
          <div
            v-if="authStore.user?.pending_email"
            class="flex flex-col gap-1.5 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700"
          >
            <span>
              Ожидает подтверждения:
              <span class="font-medium">{{ authStore.user.pending_email }}</span>
            </span>
            <button
              type="button"
              class="self-start font-medium underline underline-offset-2 hover:text-amber-900"
              @click="openEmailModal(2)"
            >
              Ввести код
            </button>
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
          <Button variant="secondary" block @click="openProfileModal">
            Редактировать профиль
          </Button>
          <Button variant="secondary" block @click="openEmailModal(1)">Изменить email</Button>
          <Button variant="secondary" block @click="openPasswordModal">Изменить пароль</Button>
          <Button variant="secondary" block @click="handleLogout">Выйти из аккаунта</Button>
        </div>
      </div>

      <div
        v-if="authStore.isAdmin"
        class="mt-6 rounded-2xl border border-neutral-200 bg-white p-6 shadow-card"
      >
        <h2 class="mb-4 text-base font-semibold text-neutral-900">Администрирование</h2>
        <RouterLink
          :to="{ name: 'stats' }"
          class="block rounded-xl border border-neutral-200 px-4 py-3 text-sm font-medium text-neutral-700 transition-colors hover:bg-neutral-50"
        >
          Статистика изображений
        </RouterLink>
      </div>
    </div>

    <!-- Edit profile modal (username, first_name, last_name) -->
    <Modal :open="showProfileModal" title="Редактировать профиль" @close="closeProfileModal">
      <h2 class="mb-5 text-base font-semibold text-neutral-900">Редактировать профиль</h2>

      <form class="flex flex-col gap-4" @submit.prevent="onUpdateProfile">
        <p
          v-if="profileServerError"
          role="alert"
          class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"
        >
          {{ profileServerError }}
        </p>

        <Field label="Имя пользователя" :error="profileUsernameError" required>
          <Input v-model="profileUsername" autocomplete="username" />
        </Field>

        <Field label="Имя" :error="firstNameError">
          <Input v-model="firstName" autocomplete="given-name" />
        </Field>

        <Field label="Фамилия" :error="lastNameError">
          <Input v-model="lastName" autocomplete="family-name" />
        </Field>

        <div class="flex gap-3">
          <Button type="button" variant="secondary" block @click="closeProfileModal">Отмена</Button>
          <Button type="submit" :loading="isProfileSubmitting" block>Сохранить</Button>
        </div>
      </form>
    </Modal>

    <!-- Change email modal (2-step) -->
    <Modal :open="showEmailModal" title="Изменить email" @close="closeEmailModal">
      <!-- Step 1: enter new email -->
      <template v-if="emailStep === 1">
        <h2 class="mb-5 text-base font-semibold text-neutral-900">Изменить email</h2>

        <form class="flex flex-col gap-4" @submit.prevent="onSubmitNewEmail">
          <p
            v-if="emailServerError"
            role="alert"
            class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"
          >
            {{ emailServerError }}
          </p>

          <Field label="Новый email" :error="newEmailError" required>
            <Input v-model="newEmail" type="email" autocomplete="email" />
          </Field>

          <div class="flex gap-3">
            <Button type="button" variant="secondary" block @click="closeEmailModal">Отмена</Button>
            <Button type="submit" :loading="isEmailSubmitting" block>Отправить код</Button>
          </div>
        </form>
      </template>

      <!-- Step 2: enter confirmation code -->
      <template v-else>
        <h2 class="mb-2 text-base font-semibold text-neutral-900">Введите код</h2>
        <p class="mb-5 text-sm text-neutral-500">
          Код отправлен на
          <span class="font-medium text-neutral-700">{{ authStore.user?.pending_email }}</span
          >. Код действителен 15 минут.
        </p>

        <form class="flex flex-col gap-4" @submit.prevent="onConfirmCode">
          <p
            v-if="codeServerError"
            role="alert"
            class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"
          >
            {{ codeServerError }}
          </p>

          <Field label="Код подтверждения" :error="codeError" required>
            <Input
              v-model="codeValue"
              inputmode="numeric"
              maxlength="6"
              placeholder="000000"
              autocomplete="one-time-code"
            />
          </Field>

          <Button type="submit" :loading="isCodeSubmitting" block>Подтвердить</Button>
          <div class="flex gap-3">
            <Button type="button" variant="secondary" block @click="emailStep = 1">
              Изменить email
            </Button>
            <Button
              type="button"
              variant="secondary"
              :loading="isResending"
              block
              @click="resendCode"
            >
              Отправить повторно
            </Button>
          </div>
        </form>
      </template>
    </Modal>

    <!-- Change password modal -->
    <Modal :open="showPasswordModal" title="Изменить пароль" @close="closePasswordModal">
      <h2 class="mb-5 text-base font-semibold text-neutral-900">Изменить пароль</h2>

      <form class="flex flex-col gap-4" @submit.prevent="onChangePassword">
        <p
          v-if="passwordServerError"
          role="alert"
          class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"
        >
          {{ passwordServerError }}
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

        <div class="flex gap-3">
          <Button type="button" variant="secondary" block @click="closePasswordModal"
            >Отмена</Button
          >
          <Button type="submit" :loading="isPasswordSubmitting" block>Сохранить</Button>
        </div>
      </form>
    </Modal>
  </AppShell>
</template>
