import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ImageListParams } from '@/api/types'

export function useFilterQuery() {
  const route = useRoute()
  const router = useRouter()

  const page = computed(() => Number(route.query.page) || 1)
  const search = computed(() => (route.query.search as string) || '')
  const dateFrom = computed(() => (route.query.date_from as string) || '')
  const dateTo = computed(() => (route.query.date_to as string) || '')
  const imageFormat = computed(() => (route.query.image_format as string) || '')
  const minSizeMb = computed(() => (route.query.min_size_mb as string) || '')
  const maxSizeMb = computed(() => (route.query.max_size_mb as string) || '')
  const minWidth = computed(() => (route.query.min_width as string) || '')
  const maxWidth = computed(() => (route.query.max_width as string) || '')
  const minHeight = computed(() => (route.query.min_height as string) || '')
  const maxHeight = computed(() => (route.query.max_height as string) || '')

  function update(patch: Record<string, string | number | undefined>) {
    const q = { ...route.query }
    for (const [k, v] of Object.entries(patch)) {
      if (v === undefined || v === '' || v === 0) {
        delete q[k]
      } else {
        q[k] = String(v)
      }
    }
    router.push({ query: q })
  }

  function setPage(p: number) {
    update({ page: p > 1 ? p : undefined })
  }

  function setSearch(s: string) {
    update({ search: s || undefined, page: undefined })
  }

  function clearAll() {
    router.push({ query: {} })
  }

  function toApiParams(): ImageListParams {
    return {
      page: page.value > 1 ? page.value : undefined,
      search: search.value || undefined,
      date_from: dateFrom.value || undefined,
      date_to: dateTo.value || undefined,
      image_format: imageFormat.value || undefined,
      min_size_mb: minSizeMb.value ? Number(minSizeMb.value) : undefined,
      max_size_mb: maxSizeMb.value ? Number(maxSizeMb.value) : undefined,
      min_width: minWidth.value ? Number(minWidth.value) : undefined,
      max_width: maxWidth.value ? Number(maxWidth.value) : undefined,
      min_height: minHeight.value ? Number(minHeight.value) : undefined,
      max_height: maxHeight.value ? Number(maxHeight.value) : undefined,
    }
  }

  return {
    page,
    search,
    dateFrom,
    dateTo,
    imageFormat,
    minSizeMb,
    maxSizeMb,
    minWidth,
    maxWidth,
    minHeight,
    maxHeight,
    setPage,
    setSearch,
    update,
    clearAll,
    toApiParams,
  }
}
