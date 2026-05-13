import { z } from 'zod'

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp', 'image/gif']
const MAX_SIZE_BYTES = 15 * 1024 * 1024

export const uploadSchema = z.object({
  title: z.string().min(1, 'Введите название').max(255, 'Максимум 255 символов'),
  description: z.string().max(1000, 'Максимум 1000 символов').optional(),
  file: z
    .instanceof(File, { message: 'Выберите файл' })
    .refine((f) => ALLOWED_TYPES.includes(f.type), 'Допустимы только JPEG, PNG, WEBP, BMP, GIF')
    .refine((f) => f.size <= MAX_SIZE_BYTES, 'Файл не должен превышать 15 МБ'),
})

export const editSchema = z.object({
  title: z.string().min(1, 'Введите название').max(255, 'Максимум 255 символов'),
  description: z.string().max(1000, 'Максимум 1000 символов').optional(),
})

export type UploadInput = z.infer<typeof uploadSchema>
export type EditInput = z.infer<typeof editSchema>
