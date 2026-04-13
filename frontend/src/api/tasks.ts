import { apiClient } from './client'
import type { ParseTask, ParseTaskCreated } from '../types'

export async function createParseTask(url: string): Promise<ParseTaskCreated> {
  const { data } = await apiClient.post<ParseTaskCreated>('/tasks/parse', { url })
  return data
}

export async function getTaskStatus(taskId: string): Promise<ParseTask> {
  const { data } = await apiClient.get<ParseTask>(`/tasks/${taskId}`)
  return data
}
