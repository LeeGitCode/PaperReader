import { apiClient } from './client'
import type {
  PaginatedResponse,
  Tag,
  TagCreatePayload,
  TagGroup,
  TagGroupListQuery,
  TagListQuery,
  TagUpdatePayload,
} from '../types'

export async function getTags(params: TagListQuery = {}): Promise<PaginatedResponse<Tag>> {
  const { data } = await apiClient.get<PaginatedResponse<Tag>>('/tags', { params })
  return data
}

export async function createTag(payload: TagCreatePayload): Promise<Tag> {
  const { data } = await apiClient.post<Tag>('/tags', payload)
  return data
}

export async function updateTag(tagId: number, payload: TagUpdatePayload): Promise<Tag> {
  const { data } = await apiClient.patch<Tag>(`/tags/${tagId}`, payload)
  return data
}

export async function deleteTag(tagId: number): Promise<void> {
  await apiClient.delete(`/tags/${tagId}`)
}

export async function getTagGroups(
  params: TagGroupListQuery = {},
): Promise<PaginatedResponse<TagGroup>> {
  const { data } = await apiClient.get<PaginatedResponse<TagGroup>>('/tag-groups', { params })
  return data
}
