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

export const forgotPasswordSchema = z.object({
  email: z.string().email('Введите корректный email'),
})

export const resetPasswordSchema = z
  .object({
    new_password: z.string().min(8, 'Минимум 8 символов'),
    new_password2: z.string(),
  })
  .refine((d) => d.new_password === d.new_password2, {
    message: 'Пароли не совпадают',
    path: ['new_password2'],
  })

export const changePasswordSchema = z
  .object({
    old_password: z.string().min(1, 'Введите текущий пароль'),
    new_password: z.string().min(8, 'Минимум 8 символов'),
    new_password2: z.string(),
  })
  .refine((d) => d.new_password === d.new_password2, {
    message: 'Пароли не совпадают',
    path: ['new_password2'],
  })

export const emailCodeSchema = z.object({
  code: z
    .string()
    .length(6, 'Код должен состоять из 6 цифр')
    .regex(/^\d{6}$/, 'Только цифры'),
})

export type EmailCodeInput = z.infer<typeof emailCodeSchema>

export const updateProfileSchema = z.object({
  username: z
    .string()
    .min(3, 'Минимум 3 символа')
    .max(150, 'Максимум 150 символов')
    .regex(/^\w+$/, 'Только буквы, цифры и _'),
  first_name: z.string().max(150, 'Максимум 150 символов').or(z.literal('')),
  last_name: z.string().max(150, 'Максимум 150 символов').or(z.literal('')),
})

export const changeEmailSchema = z.object({
  email: z.string().email('Введите корректный email'),
})

export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>
export type ResetPasswordInput = z.infer<typeof resetPasswordSchema>
export type ChangePasswordInput = z.infer<typeof changePasswordSchema>
export type UpdateProfileInput = z.infer<typeof updateProfileSchema>
