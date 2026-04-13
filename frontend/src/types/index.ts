export type PaperStatus = 'to_read' | 'reading' | 'completed'

export type SortOrder = 'asc' | 'desc'

export type PaperSortBy =
  | 'priority'
  | 'updated_at'
  | 'created_at'
  | 'pub_year'
  | 'year'
  | 'year_desc'
  | 'last_read_at'
  | 'last_read_desc'
  | 'title'
  | 'aka_name'
  | 'status'

export type PaperSortPreset = 'default' | 'priority_desc' | 'year_desc' | 'last_read_desc'

export interface TagGroup {
  id: number
  code: string
  display_name: string
  description: string | null
  created_at: string
}

export interface Tag {
  id: number
  name: string
  normalized_name: string
  color: string
  description: string | null
  created_at: string
  tag_group: TagGroup | null
}

export interface Paper {
  id: number
  title: string
  aka_name: string | null
  authors_display: string | null
  venue: string | null
  pub_year: number | null
  pub_month: number | null
  status: PaperStatus
  priority: number
  pdf_path: string | null
  pdf_url: string | null
  code_url: string | null
  notes: string | null
  last_read_at: string | null
  metadata_json: Record<string, unknown>
  arxiv_id: string | null
  doi: string | null
  is_archived: boolean
  created_at: string
  updated_at: string
  tags: Tag[]
}

export interface PaperCreatePayload {
  title: string
  aka_name?: string | null
  authors_display?: string | null
  venue?: string | null
  pub_year?: number | null
  pub_month?: number | null
  status?: PaperStatus
  priority?: number
  pdf_path?: string | null
  pdf_url?: string | null
  code_url?: string | null
  notes?: string | null
  last_read_at?: string | null
  metadata_json?: Record<string, unknown>
  arxiv_id?: string | null
  doi?: string | null
  is_archived?: boolean
  tag_ids?: number[]
}

export type PaperUpdatePayload = Partial<PaperCreatePayload>

export interface ParsedPaperDraft {
  title: string
  authors: string
  authors_display: string
  year: number | null
  pub_year: number | null
  venue: string
  pdf_path: string
  pdf_url: string
  status: PaperStatus
  priority: number
  arxiv_id?: string
  doi?: string
}

export interface PaginationMeta {
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface PaginatedResponse<T> {
  items: T[]
  meta: PaginationMeta
}

export interface ApiErrorPayload {
  error: {
    code: string
    message: string
    details: unknown
  }
}

export type ParseTaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface ParseTaskCreated {
  task_id: string
}

export interface ParseTask {
  task_id: string
  status: ParseTaskStatus
  progress: number
  result: ParsedPaperDraft | null
  error_msg: string | null
}

export interface PaperListQuery {
  q?: string
  status?: PaperStatus
  priority?: number
  tag_id?: number[]
  is_archived?: boolean
  page?: number
  per_page?: number
  sort_by?: PaperSortBy
  sort_order?: SortOrder
}

export interface TagListQuery {
  q?: string
  tag_group_id?: number
  page?: number
  per_page?: number
  sort_by?: 'name' | 'normalized_name' | 'created_at'
  sort_order?: SortOrder
}

export interface TagCreatePayload {
  name: string
  normalized_name?: string | null
  color?: string | null
  description?: string | null
  tag_group_id?: number | null
}

export type TagUpdatePayload = Partial<TagCreatePayload>

export interface TagGroupListQuery {
  q?: string
  page?: number
  per_page?: number
  sort_by?: 'code' | 'display_name' | 'created_at'
  sort_order?: SortOrder
}
