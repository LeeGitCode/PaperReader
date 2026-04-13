import axios, { AxiosError } from 'axios'
import type { ApiErrorPayload } from '../types'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api',
  timeout: 12_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export function getApiErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const payload = error.response?.data as ApiErrorPayload | undefined
    return payload?.error?.message ?? error.message
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'Unknown API error.'
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorPayload>) => {
    const message = error.response?.data?.error?.message ?? error.message
    console.warn(`[PaperReader API] ${message}`)
    return Promise.reject(error)
  },
)
