import { api } from './axios'

export async function exportBackup(): Promise<{ blob: Blob; filename: string }> {
  const res = await api.get('/system/backup/export/', { responseType: 'blob' })
  const cd: string = res.headers['content-disposition'] ?? ''
  const match = cd.match(/filename="?([^"]+)"?/)
  const filename = match?.[1] ?? 'stocker_backup.zip'
  return { blob: res.data, filename }
}

export async function importBackup(
  archive: File,
): Promise<{ detail: string; records_inserted: number }> {
  const form = new FormData()
  form.append('archive', archive)
  const res = await api.post('/system/backup/import/', form)
  return res.data
}
