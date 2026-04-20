import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type LoginPayload, type RegisterPayload } from '@/api/auth'
import type { User } from '@/api/types'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const token = ref<string | null>(null)
    const user = ref<User | null>(null)

    const isAuthenticated = computed(() => !!token.value)
    const isAdmin = computed(() => user.value?.role === 'admin')

    async function login(payload: LoginPayload) {
      const { data } = await authApi.login(payload)
      token.value = data.token
      user.value = data.user
      return data
    }

    async function register(payload: RegisterPayload) {
      const { data } = await authApi.register(payload)
      token.value = data.token
      user.value = data.user
      return data
    }

    async function logout() {
      try {
        await authApi.logout()
      } finally {
        token.value = null
        user.value = null
      }
    }

    async function fetchMe() {
      const { data } = await authApi.me()
      user.value = data
    }

    function clear() {
      token.value = null
      user.value = null
    }

    return { token, user, isAuthenticated, isAdmin, login, register, logout, fetchMe, clear }
  },
  {
    persist: {
      pick: ['token'],
    },
  },
)
