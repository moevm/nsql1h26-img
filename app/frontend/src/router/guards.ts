import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function requiresAuth(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext,
) {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) {
    next({ name: 'login', query: { next: to.fullPath } })
  } else {
    next()
  }
}

export function guestOnly(
  _to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext,
) {
  const auth = useAuthStore()
  if (auth.isAuthenticated) {
    next({ name: 'gallery' })
  } else {
    next()
  }
}
