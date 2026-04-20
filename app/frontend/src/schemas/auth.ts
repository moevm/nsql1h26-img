import { z } from 'zod'

export const registerSchema = z
  .object({
    username: z
      .string()
      .min(3, 'Минимум 3 символа')
      .max(30, 'Максимум 30 символов')
      .regex(/^\w+$/, 'Только буквы, цифры и _'),
    email: z.string().email('Введите корректный email'),
    password: z.string().min(8, 'Минимум 8 символов'),
    password2: z.string(),
  })
  .refine((d) => d.password === d.password2, {
    message: 'Пароли не совпадают',
    path: ['password2'],
  })

export const loginSchema = z.object({
  login: z.string().min(1, 'Введите логин или email'),
  password: z.string().min(1, 'Введите пароль'),
})

export type RegisterInput = z.infer<typeof registerSchema>
export type LoginInput = z.infer<typeof loginSchema>
