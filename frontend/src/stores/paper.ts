import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { useIntervalFn } from '@vueuse/core'
import {
  addPaper as addPaperRequest,
  createParseTask,
  deletePaper as deletePaperRequest,
  deleteTag as deleteTagRequest,
  createTag as createTagRequest,
  getApiErrorMessage,
  getPapers,
  getTags,
  getTaskStatus,
  updatePaper as updatePaperRequest,
  updatePaperStatus,
} from '../api'
import type {
  PaginatedResponse,
  PaginationMeta,
  Paper,
  PaperCreatePayload,
  PaperListQuery,
  PaperSortBy,
  PaperSortPreset,
  PaperStatus,
  PaperUpdatePayload,
  ParseTask,
  SortOrder,
  Tag,
  TagCreatePayload,
} from '../types'

const defaultMeta: PaginationMeta = {
  page: 1,
  per_page: 20,
  total: 0,
  total_pages: 0,
}

export const usePaperStore = defineStore('paper', () => {
  const papers = ref<Paper[]>([])
  const tags = ref<Tag[]>([])
  const meta = ref<PaginationMeta>({ ...defaultMeta })

  const page = ref(1)
  const perPage = ref(20)
  const searchQuery = ref('')
  const selectedStatus = ref<PaperStatus | undefined>()
  const selectedTagId = ref<number | undefined>()
  const selectedPriority = ref<number | undefined>()
  const sortBy = ref<PaperSortBy>('updated_at')
  const sortOrder = ref<SortOrder>('desc')
  const sortPreset = ref<PaperSortPreset>('default')

  const isLoadingPapers = ref(false)
  const isLoadingTags = ref(false)
  const isSavingPaper = ref(false)
  const isSavingTag = ref(false)
  const parseTask = ref<ParseTask | null>(null)
  const parseTaskId = ref<string | null>(null)
  const isStartingParseTask = ref(false)
  const parseTaskMessage = ref<string | null>(null)
  const errorMessage = ref<string | null>(null)

  const parsePolling = useIntervalFn(
    async () => {
      await pollParseTask()
    },
    1000,
    { immediate: false },
  )

  const hasActiveFilters = computed(
    () =>
      Boolean(searchQuery.value.trim()) ||
      selectedStatus.value !== undefined ||
      selectedTagId.value !== undefined ||
      selectedPriority.value !== undefined,
  )

  const paperQuery = computed<PaperListQuery>(() => ({
    q: searchQuery.value.trim() || undefined,
    status: selectedStatus.value,
    priority: selectedPriority.value,
    tag_id: selectedTagId.value === undefined ? undefined : [selectedTagId.value],
    is_archived: false,
    page: page.value,
    per_page: perPage.value,
    sort_by: sortBy.value,
    sort_order: sortOrder.value,
  }))

  function applyPaperResponse(response: PaginatedResponse<Paper>) {
    papers.value = response.items
    meta.value = response.meta
  }

  async function fetchPapers() {
    isLoadingPapers.value = true
    errorMessage.value = null

    try {
      applyPaperResponse(await getPapers(paperQuery.value))
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error)
    } finally {
      isLoadingPapers.value = false
    }
  }

  async function fetchTags() {
    isLoadingTags.value = true
    errorMessage.value = null

    try {
      const response = await getTags({ per_page: 200, sort_by: 'name', sort_order: 'asc' })
      tags.value = response.items
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error)
    } finally {
      isLoadingTags.value = false
    }
  }

  async function setPage(nextPage: number) {
    page.value = Math.max(1, nextPage)
    await fetchPapers()
  }

  async function setPerPage(nextPerPage: number) {
    perPage.value = nextPerPage
    page.value = 1
    await fetchPapers()
  }

  async function setSearchQuery(query: string) {
    searchQuery.value = query
    page.value = 1
    await fetchPapers()
  }

  async function setStatusFilter(status: PaperStatus | undefined) {
    selectedStatus.value = status
    page.value = 1
    await fetchPapers()
  }

  async function setTagFilter(tagId: number | undefined) {
    selectedTagId.value = tagId
    page.value = 1
    await fetchPapers()
  }

  async function setPriorityFilter(priority: number | undefined) {
    selectedPriority.value = priority
    page.value = 1
    await fetchPapers()
  }

  async function setSort(nextSortBy: PaperSortBy, nextSortOrder: SortOrder = sortOrder.value) {
    sortBy.value = nextSortBy
    sortOrder.value = nextSortOrder
    sortPreset.value = toSortPreset(nextSortBy, nextSortOrder)
    page.value = 1
    await fetchPapers()
  }

  async function setSortPreset(nextPreset: PaperSortPreset) {
    sortPreset.value = nextPreset

    if (nextPreset === 'priority_desc') {
      sortBy.value = 'priority'
      sortOrder.value = 'desc'
    } else if (nextPreset === 'year_desc') {
      sortBy.value = 'year_desc'
      sortOrder.value = 'desc'
    } else if (nextPreset === 'last_read_desc') {
      sortBy.value = 'last_read_desc'
      sortOrder.value = 'desc'
    } else {
      sortBy.value = 'updated_at'
      sortOrder.value = 'desc'
    }

    page.value = 1
    await fetchPapers()
  }

  async function resetFilters() {
    searchQuery.value = ''
    selectedStatus.value = undefined
    selectedTagId.value = undefined
    selectedPriority.value = undefined
    page.value = 1
    await fetchPapers()
  }

  async function changePaperStatus(paperId: number, status: PaperStatus) {
    errorMessage.value = null

    try {
      const updatedPaper = await updatePaperStatus(paperId, status)
      papers.value = papers.value.map((paper) => (paper.id === paperId ? updatedPaper : paper))
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error)
    }
  }

  async function createPaper(payload: PaperCreatePayload) {
    isSavingPaper.value = true
    errorMessage.value = null

    try {
      await addPaperRequest(payload)
      page.value = 1
      await fetchPapers()
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error)
      throw error
    } finally {
      isSavingPaper.value = false
    }
  }

  async function updatePaper(paperId: number, payload: PaperUpdatePayload) {
    isSavingPaper.value = true
    errorMessage.value = null

    try {
      const updatedPaper = await updatePaperRequest(paperId, payload)
      papers.value = papers.value.map((paper) => (paper.id === paperId ? updatedPaper : paper))
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error)
      throw error
    } finally {
      isSavingPaper.value = false
    }
  }

  async function deletePaper(paperId: number) {
    errorMessage.value = null

    try {
      await deletePaperRequest(paperId)
      papers.value = papers.value.filter((paper) => paper.id !== paperId)
      meta.value = { ...meta.value, total: Math.max(0, meta.value.total - 1) }
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error)
      throw error
    }
  }

  async function createTag(payload: TagCreatePayload) {
    isSavingTag.value = true
    errorMessage.value = null

    try {
      const tag = await createTagRequest(payload)
      tags.value = [...tags.value, tag].sort((a, b) => a.name.localeCompare(b.name))
      return tag
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error)
      throw error
    } finally {
      isSavingTag.value = false
    }
  }

  async function deleteTag(tagId: number) {
    errorMessage.value = null

    try {
      await deleteTagRequest(tagId)
      tags.value = tags.value.filter((tag) => tag.id !== tagId)
      papers.value = papers.value.map((paper) => ({
        ...paper,
        tags: paper.tags.filter((tag) => tag.id !== tagId),
      }))

      if (selectedTagId.value === tagId) {
        selectedTagId.value = undefined
        page.value = 1
        await fetchPapers()
      }
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error)
      throw error
    }
  }

  async function startParseTask(url: string) {
    isStartingParseTask.value = true
    errorMessage.value = null
    parseTaskMessage.value = '任务初始化中...'
    parseTask.value = null

    try {
      const created = await createParseTask(url)
      parseTaskId.value = created.task_id
      parseTask.value = {
        task_id: created.task_id,
        status: 'pending',
        progress: 0,
        result: null,
        error_msg: null,
      }
      parseTaskMessage.value = '正在抓取元数据...'
      parsePolling.resume()
      await pollParseTask()
    } catch (error) {
      parseTaskMessage.value = null
      errorMessage.value = getApiErrorMessage(error)
      throw error
    } finally {
      isStartingParseTask.value = false
    }
  }

  async function pollParseTask() {
    if (!parseTaskId.value) {
      parsePolling.pause()
      return
    }

    try {
      const task = await getTaskStatus(parseTaskId.value)
      parseTask.value = task

      if (task.status === 'completed') {
        parseTaskMessage.value = '解析完成！'
        parsePolling.pause()
      } else if (task.status === 'failed') {
        parseTaskMessage.value = task.error_msg ?? '解析失败'
        parsePolling.pause()
      } else if (task.status === 'processing') {
        parseTaskMessage.value = '正在抓取元数据...'
      } else {
        parseTaskMessage.value = '任务初始化中...'
      }
    } catch (error) {
      parsePolling.pause()
      parseTaskMessage.value = null
      errorMessage.value = getApiErrorMessage(error)
      throw error
    }
  }

  function stopParsePolling() {
    parsePolling.pause()
  }

  function resetParseTask() {
    parsePolling.pause()
    parseTask.value = null
    parseTaskId.value = null
    parseTaskMessage.value = null
    isStartingParseTask.value = false
  }

  return {
    papers,
    tags,
    meta,
    page,
    perPage,
    searchQuery,
    selectedStatus,
    selectedTagId,
    selectedPriority,
    sortBy,
    sortOrder,
    sortPreset,
    isLoadingPapers,
    isLoadingTags,
    isSavingPaper,
    isSavingTag,
    parseTask,
    parseTaskId,
    isStartingParseTask,
    isPollingParseTask: parsePolling.isActive,
    parseTaskMessage,
    errorMessage,
    hasActiveFilters,
    paperQuery,
    fetchPapers,
    fetchTags,
    setPage,
    setPerPage,
    setSearchQuery,
    setStatusFilter,
    setTagFilter,
    setPriorityFilter,
    setSort,
    setSortPreset,
    resetFilters,
    changePaperStatus,
    createPaper,
    updatePaper,
    deletePaper,
    createTag,
    deleteTag,
    startParseTask,
    pollParseTask,
    stopParsePolling,
    resetParseTask,
  }
})

function toSortPreset(sortBy: PaperSortBy, sortOrder: SortOrder): PaperSortPreset {
  if (sortBy === 'priority' && sortOrder === 'desc') {
    return 'priority_desc'
  }

  if (sortBy === 'year_desc' || (sortBy === 'year' && sortOrder === 'desc')) {
    return 'year_desc'
  }

  if (sortBy === 'last_read_desc' || (sortBy === 'last_read_at' && sortOrder === 'desc')) {
    return 'last_read_desc'
  }

  return 'default'
}
