import { ref, type Ref } from 'vue'

export type AsyncState = 'idle' | 'loading' | 'error' | 'empty' | 'ready'

export interface AsyncResult<T> {
  state: Ref<AsyncState>
  data: Ref<T | null>
  error: Ref<string | null>
  run: (fn: () => Promise<T>, isEmpty?: (data: T) => boolean) => Promise<void>
}

export function useAsync<T>(): AsyncResult<T> {
  const state = ref<AsyncState>('idle')
  const data = ref<T | null>(null) as Ref<T | null>
  const error = ref<string | null>(null)

  async function run(fn: () => Promise<T>, isEmpty?: (d: T) => boolean) {
    state.value = 'loading'
    error.value = null
    try {
      const result = await fn()
      data.value = result
      state.value = isEmpty?.(result) ? 'empty' : 'ready'
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Произошла ошибка'
      state.value = 'error'
    }
  }

  return { state, data, error, run }
}
