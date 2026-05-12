<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import AuthLayout from '@/layout/AuthLayout.vue'
import Logo from '@/layout/Logo.vue'
import Button from '@/components/ui/Button.vue'
import Field from '@/components/ui/Field.vue'
import Input from '@/components/ui/Input.vue'
import { authApi } from '@/api/auth'
import { mapDrfErrors } from '@/api/axios'
import { resetPasswordSchema } from '@/schemas/auth'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const route = useRoute()
const { success } = useToast()

const uid = ref<string>('')
const token = ref<string>('')
const serverError = ref<string | null>(null)

onMounted(() => {
  const u = route.query.uid as string | undefined
  const t = route.query.token as string | undefined
  if (!u || !t) {
    router.replace({ name: 'forgot-password' })
    return
  }
  uid.value = u
  token.value = t
})

const { handleSubmit, isSubmitting, setErrors } = useForm({
  validationSchema: toTypedSchema(resetPasswordSchema),
})

const { value: newPassword, errorMessage: newPasswordError } =
  useField<string>('new_password')
const { value: newPassword2, errorMessage: newPassword2Error } =
  useField<string>('new_password2')

const onSubmit = handleSubmit(async (values) => {
  serverError.value = null
  try {
    await authApi.confirmPasswordReset({
      uid: uid.value,
      token: token.value,
      new_password: values.new_password,
      new_password2: values.new_password2,
    })
    success('Пароль успешно изменён')
    router.push({ name: 'login' })
  } catch (err) {
    serverError.value =
      mapDrfErrors(err, setErrors) ?? 'Ссылка недействительна или срок её действия истёк'
  }
})
</script>

<template>
  <AuthLayout>
    <div class="w-full max-w-sm">
      <div class="mb-8 flex flex-col items-center gap-2 text-center">
        <Logo />
        <p class="mt-2 text-sm text-neutral-500">Новый пароль</p>
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

        <Field label="Новый пароль" :error="newPasswordError" required>
          <Input
            v-model="newPassword"
            type="password"
            placeholder="••••••••"
            autocomplete="new-password"
          />
        </Field>

        <Field label="Повторите пароль" :error="newPassword2Error" required>
          <Input
            v-model="newPassword2"
            type="password"
            placeholder="••••••••"
            autocomplete="new-password"
          />
        </Field>

        <Button type="submit" :loading="isSubmitting" block>Сохранить пароль</Button>
      </form>

      <p class="mt-6 text-center text-sm text-neutral-500">
        <RouterLink to="/login" class="font-medium text-neutral-900 hover:underline">
          Вернуться к входу
        </RouterLink>
      </p>
    </div>
  </AuthLayout>
</template>
