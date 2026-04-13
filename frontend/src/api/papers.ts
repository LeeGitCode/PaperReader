import { apiClient } from './client'
import type {
  PaginatedResponse,
  Paper,
  PaperCreatePayload,
  PaperListQuery,
  PaperStatus,
  PaperUpdatePayload,
} from '../types'

export async function getPapers(params: PaperListQuery = {}): Promise<PaginatedResponse<Paper>> {
  const { data } = await apiClient.get<PaginatedResponse<Paper>>('/papers', {
    params,
    paramsSerializer: {
      indexes: null,
    },
  })

  return data
}

export async function getPaper(paperId: number): Promise<Paper> {
  const { data } = await apiClient.get<Paper>(`/papers/${paperId}`)
  return data
}

export async function addPaper(payload: PaperCreatePayload): Promise<Paper> {
  const { data } = await apiClient.post<Paper>('/papers', payload)
  return data
}

export async function updatePaper(paperId: number, payload: PaperUpdatePayload): Promise<Paper> {
  const { data } = await apiClient.patch<Paper>(`/papers/${paperId}`, payload)
  return data
}

export async function updatePaperStatus(paperId: number, status: PaperStatus): Promise<Paper> {
  return updatePaper(paperId, { status })
}

export async function deletePaper(paperId: number): Promise<void> {
  await apiClient.delete(`/papers/${paperId}`)
}
