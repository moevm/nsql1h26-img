import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { requiresAuth, guestOnly } from '@/router/guards'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'gallery',
    component: () => import('@/views/GalleryView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    beforeEnter: guestOnly,
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    beforeEnter: guestOnly,
  },
  {
    path: '/register/success',
    name: 'register-success',
    component: () => import('@/views/RegisterSuccessView.vue'),
    beforeEnter: requiresAuth,
  },
  {
    path: '/favorites',
    name: 'favorites',
    component: () => import('@/views/FavoritesView.vue'),
    beforeEnter: requiresAuth,
  },
  {
    path: '/upload',
    name: 'upload',
    component: () => import('@/views/UploadView.vue'),
    beforeEnter: requiresAuth,
  },
  {
    path: '/my',
    name: 'my-images',
    component: () => import('@/views/MyImagesView.vue'),
    beforeEnter: requiresAuth,
  },
  {
    path: '/users/:username',
    name: 'public-profile',
    component: () => import('@/views/PublicProfileView.vue'),
  },
  {
    path: '/images/:id',
    name: 'image-detail',
    component: () => import('@/views/ImageDetailView.vue'),
  },
  {
    path: '/images/:id/edit',
    name: 'edit-image',
    component: () => import('@/views/EditImageView.vue'),
    beforeEnter: requiresAuth,
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    beforeEnter: requiresAuth,
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPasswordView.vue'),
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/views/ResetPasswordView.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})
