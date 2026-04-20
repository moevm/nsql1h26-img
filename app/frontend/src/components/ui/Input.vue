<script setup lang="ts">
import { computed, useId } from 'vue'

interface Props {
  id?: string
  label?: string
  type?: string
  placeholder?: string
  autocomplete?: string
  disabled?: boolean
  required?: boolean
  error?: string
  hint?: string
}

const {
  id,
  label,
  type = 'text',
  placeholder,
  autocomplete,
  disabled = false,
  required = false,
  error,
  hint,
} = defineProps<Props>()

const model = defineModel<string>({ default: '' })

const autoId = useId()
const inputId = computed(() => id ?? `input-${autoId}`)
const hintId = computed(() => `${inputId.value}-hint`)
const errorId = computed(() => `${inputId.value}-error`)

const describedBy = computed(() => {
  const ids: string[] = []
  if (hint) ids.push(hintId.value)
  if (error) ids.push(errorId.value)
  return ids.length ? ids.join(' ') : undefined
})
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label v-if="label" :for="inputId" class="text-sm font-medium text-neutral-800">
      {{ label }}
      <span v-if="required" class="text-neutral-500" aria-hidden="true">*</span>
    </label>

    <input
      :id="inputId"
      v-model="model"
      :type="type"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :disabled="disabled"
      :required="required"
      :aria-invalid="error ? true : undefined"
      :aria-describedby="describedBy"
      class="w-full rounded-xl border border-neutral-200 bg-white px-3.5 py-2.5 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-neutral-400 focus:outline-none focus:ring-2 focus:ring-neutral-900/10 disabled:cursor-not-allowed disabled:bg-neutral-50 disabled:text-neutral-400"
      :class="error ? 'border-red-400 focus:border-red-500 focus:ring-red-500/10' : ''"
    />

    <p v-if="hint && !error" :id="hintId" class="text-xs text-neutral-500">
      {{ hint }}
    </p>
    <p v-if="error" :id="errorId" class="text-xs text-red-600" role="alert">
      {{ error }}
    </p>
  </div>
</template>
