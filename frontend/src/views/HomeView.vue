<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import {
  BookOpen,
  CheckCircle2,
  CircleDot,
  Clock3,
  FilePlus2,
  FolderOpen,
  Library,
  Loader2,
  RefreshCw,
  Search,
  SlidersHorizontal,
  Tags,
  Trash2,
} from 'lucide-vue-next'
import { useDebounceFn } from '@vueuse/core'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import PaperList from '../components/PaperList.vue'
import PaperModal from '../components/PaperModal.vue'
import TagModal from '../components/TagModal.vue'
import { usePaperStore } from '../stores/paper'
import type {
  Paper,
  PaperCreatePayload,
  PaperSortPreset,
  PaperStatus,
  PaperUpdatePayload,
} from '../types'

const paperStore = usePaperStore()
const {
  papers,
  tags,
  meta,
  searchQuery,
  selectedStatus,
  selectedTagId,
  sortPreset,
  isLoadingPapers,
  isLoadingTags,
  isSavingPaper,
  isSavingTag,
  errorMessage,
  hasActiveFilters,
} = storeToRefs(paperStore)

const isPaperModalOpen = ref(false)
const isTagModalOpen = ref(false)
const editingPaper = ref<Paper | null>(null)
const confirmDialog = ref<{
  open: boolean
  title: string
  points: string[]
  confirmLabel: string
  type: 'paper' | 'tag' | null
  targetId: number | null
}>({
  open: false,
  title: '',
  points: [],
  confirmLabel: 'Delete',
  type: null,
  targetId: null,
})
const isDeleting = ref(false)

const statusFilters: Array<{
  label: string
  value: PaperStatus | undefined
  icon: typeof Library
}> = [
  { label: 'All Papers', value: undefined, icon: Library },
  { label: 'ToRead', value: 'to_read', icon: Clock3 },
  { label: 'Reading', value: 'reading', icon: CircleDot },
  { label: 'Completed', value: 'completed', icon: CheckCircle2 },
]

const sortOptions: Array<{ label: string; value: PaperSortPreset }> = [
  { label: 'Default', value: 'default' },
  { label: 'Priority', value: 'priority_desc' },
  { label: 'Year', value: 'year_desc' },
  { label: 'Read', value: 'last_read_desc' },
]

const activeStatusLabel = computed(
  () => statusFilters.find((item) => item.value === selectedStatus.value)?.label ?? 'All Papers',
)

const activeTagName = computed(() => {
  if (selectedTagId.value === undefined) {
    return 'All Tags'
  }

  return tags.value.find((tag) => tag.id === selectedTagId.value)?.name ?? 'Selected Tag'
})

const debouncedSearch = useDebounceFn((value: string) => {
  void paperStore.setSearchQuery(value)
}, 280)

function handleSearchInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  searchQuery.value = value
  debouncedSearch(value)
}

function openCreateModal() {
  editingPaper.value = null
  isPaperModalOpen.value = true
}

function openEditModal(paper: Paper) {
  editingPaper.value = paper
  isPaperModalOpen.value = true
}

function closePaperModal() {
  isPaperModalOpen.value = false
  editingPaper.value = null
}

async function handlePaperSubmit(payload: PaperCreatePayload | PaperUpdatePayload, paperId?: number) {
  if (paperId) {
    await paperStore.updatePaper(paperId, payload)
  } else {
    await paperStore.createPaper(payload as PaperCreatePayload)
  }

  closePaperModal()
}

function handleSortChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value as PaperSortPreset
  void paperStore.setSortPreset(value)
}

function openTagModal() {
  isTagModalOpen.value = true
}

function closeTagModal() {
  isTagModalOpen.value = false
}

async function handleCreateTag(name: string) {
  await paperStore.createTag({ name })
  closeTagModal()
}

function askDeletePaper(paperId: number) {
  confirmDialog.value = {
    open: true,
    title: 'Delete this paper?',
    points: [
      'This paper will be permanently removed from your library.',
      'Its tag links and local metadata will be deleted together.',
      'This action cannot be undone.',
    ],
    confirmLabel: 'Delete paper',
    type: 'paper',
    targetId: paperId,
  }
}

function askDeleteTag(tagId: number, tagName: string) {
  confirmDialog.value = {
    open: true,
    title: `Delete tag "${tagName}"?`,
    points: [
      'This tag will be removed from the Tags list.',
      'The tag marker will be removed from every paper that uses it.',
      'Paper-tag index records will be cleaned up automatically.',
      'Papers themselves will not be deleted.',
    ],
    confirmLabel: 'Delete tag',
    type: 'tag',
    targetId: tagId,
  }
}

function closeConfirmDialog() {
  if (isDeleting.value) {
    return
  }

  confirmDialog.value.open = false
}

async function handleConfirmDelete() {
  if (!confirmDialog.value.type || confirmDialog.value.targetId === null) {
    return
  }

  isDeleting.value = true
  try {
    if (confirmDialog.value.type === 'paper') {
      await paperStore.deletePaper(confirmDialog.value.targetId)
    } else {
      await paperStore.deleteTag(confirmDialog.value.targetId)
    }

    confirmDialog.value.open = false
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => {
  void paperStore.fetchTags()
  void paperStore.fetchPapers()
})
</script>

<template>
  <main class="min-h-screen bg-[#f6f1e8] text-slate-950">
    <div class="flex min-h-screen">
      <aside
        class="hidden w-80 shrink-0 border-r border-stone-200 bg-[#fbf8f1]/95 px-5 py-6 shadow-[12px_0_40px_rgba(66,54,38,0.05)] lg:flex lg:flex-col"
      >
        <div class="flex items-center gap-3 px-2">
          <div class="grid size-11 place-items-center rounded-2xl bg-slate-950 text-stone-50">
            <BookOpen class="size-5" />
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.26em] text-stone-500">PaperReader</p>
            <h1 class="text-lg font-semibold tracking-tight">Research OS</h1>
          </div>
        </div>

        <label class="mt-8 flex items-center gap-3 rounded-2xl border border-stone-200 bg-white px-4 py-3 shadow-sm">
          <Search class="size-4 text-stone-400" />
          <input
            :value="searchQuery"
            type="search"
            placeholder="Search title, AKA, venue..."
            class="w-full bg-transparent text-sm text-slate-900 outline-none placeholder:text-stone-400"
            @input="handleSearchInput"
          />
        </label>

        <nav class="mt-7 space-y-2">
          <p class="px-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-400">Library</p>
          <button
            v-for="item in statusFilters"
            :key="item.label"
            type="button"
            class="flex w-full items-center justify-between rounded-2xl px-3 py-2.5 text-left text-sm transition"
            :class="
              selectedStatus === item.value
                ? 'bg-slate-950 text-stone-50 shadow-lg shadow-slate-950/10'
                : 'text-stone-600 hover:bg-stone-100 hover:text-slate-950'
            "
            @click="paperStore.setStatusFilter(item.value)"
          >
            <span class="flex items-center gap-3">
              <component :is="item.icon" class="size-4" />
              {{ item.label }}
            </span>
          </button>
        </nav>

        <section class="mt-7 min-h-0 flex-1 overflow-hidden">
          <div class="flex items-center justify-between px-2">
            <p class="text-xs font-semibold uppercase tracking-[0.22em] text-stone-400">Tags</p>
            <div class="flex items-center gap-2">
              <Loader2
                v-if="isLoadingTags || isSavingTag"
                class="size-3.5 animate-spin text-stone-400"
              />
              <button
                type="button"
                class="rounded-full border border-stone-200 bg-white px-2.5 py-1 text-[11px] font-semibold text-stone-500 transition hover:border-stone-300 hover:text-slate-950"
                title="Create Tag"
                @click="openTagModal"
              >
                New
              </button>
            </div>
          </div>

          <div class="mt-2 max-h-[42vh] space-y-1 overflow-y-auto pr-1">
            <button
              type="button"
              class="flex w-full items-center justify-between rounded-2xl px-3 py-2.5 text-left text-sm transition"
              :class="
                selectedTagId === undefined
                  ? 'bg-stone-900 text-stone-50'
                  : 'text-stone-600 hover:bg-stone-100 hover:text-slate-950'
              "
              @click="paperStore.setTagFilter(undefined)"
            >
              <span class="flex items-center gap-3">
                <FolderOpen class="size-4" />
                All Tags
              </span>
            </button>

            <div
              v-for="tag in tags"
              :key="tag.id"
              class="flex w-full items-center justify-between rounded-2xl px-3 py-2.5 text-left text-sm transition"
              :class="
                selectedTagId === tag.id
                  ? 'bg-stone-900 text-stone-50'
                  : 'text-stone-600 hover:bg-stone-100 hover:text-slate-950'
              "
            >
              <button
                type="button"
                class="flex min-w-0 flex-1 items-center gap-3 text-left"
                @click="paperStore.setTagFilter(tag.id)"
              >
                <span
                  class="size-2.5 shrink-0 rounded-full"
                  :style="{ backgroundColor: tag.color }"
                />
                <span class="truncate">{{ tag.name }}</span>
              </button>
              <button
                type="button"
                class="ml-2 rounded-lg p-1.5 opacity-60 transition hover:bg-red-50 hover:text-red-600 hover:opacity-100"
                title="Delete Tag"
                @click.stop="askDeleteTag(tag.id, tag.name)"
              >
                <Trash2 class="size-3.5" />
              </button>
            </div>
          </div>
        </section>
      </aside>

      <section class="flex min-w-0 flex-1 flex-col">
        <header class="border-b border-stone-200 bg-[#fffdf8]/85 px-5 py-5 backdrop-blur md:px-8">
          <div class="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <div class="flex flex-wrap items-center gap-2 text-sm text-stone-500">
                <span>{{ activeStatusLabel }}</span>
                <span>/</span>
                <span>{{ activeTagName }}</span>
              </div>
              <h2 class="mt-2 text-3xl font-semibold tracking-[-0.04em] text-slate-950 md:text-4xl">
                Paper Library
              </h2>
            </div>

            <div class="flex flex-wrap items-center gap-3">
              <button
                type="button"
                class="inline-flex items-center gap-2 rounded-2xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-medium text-stone-700 shadow-sm transition hover:border-stone-300 hover:text-slate-950"
                @click="paperStore.fetchPapers"
              >
                <RefreshCw class="size-4" :class="isLoadingPapers ? 'animate-spin' : ''" />
                Refresh
              </button>

              <label
                class="inline-flex items-center gap-2 rounded-2xl border border-stone-200 bg-white px-4 py-2.5 text-sm font-medium text-stone-700 shadow-sm transition focus-within:border-stone-400"
              >
                <Tags class="size-4 text-stone-400" />
                <select
                  :value="sortPreset"
                  class="bg-transparent text-sm font-medium text-stone-700 outline-none"
                  @change="handleSortChange"
                >
                  <option v-for="option in sortOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <button
                type="button"
                class="inline-flex items-center gap-2 rounded-2xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-stone-50 shadow-lg shadow-slate-950/15 transition hover:bg-slate-800"
                @click="openCreateModal"
              >
                <FilePlus2 class="size-4" />
                New Paper
              </button>
            </div>
          </div>

          <div class="mt-5 flex flex-wrap items-center gap-3 text-sm text-stone-500">
            <span class="rounded-full border border-stone-200 bg-white px-3 py-1.5">
              {{ meta.total }} papers
            </span>
            <span class="rounded-full border border-stone-200 bg-white px-3 py-1.5">
              Page {{ meta.page || 1 }} / {{ meta.total_pages || 0 }}
            </span>
            <button
              v-if="hasActiveFilters"
              type="button"
              class="inline-flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 font-medium text-amber-800"
              @click="paperStore.resetFilters"
            >
              <SlidersHorizontal class="size-3.5" />
              Reset filters
            </button>
          </div>
        </header>

        <div class="flex-1 overflow-y-auto px-5 py-6 md:px-8">
          <div
            v-if="errorMessage"
            class="mb-5 rounded-3xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700"
          >
            {{ errorMessage }}
          </div>

          <PaperList
            :papers="papers"
            :meta="meta"
            :is-loading="isLoadingPapers"
            @edit="openEditModal"
            @delete="askDeletePaper"
            @status-change="paperStore.changePaperStatus"
            @page-change="paperStore.setPage"
          />
        </div>
      </section>
    </div>

    <PaperModal
      :open="isPaperModalOpen"
      :paper="editingPaper"
      :tags="tags"
      :is-saving="isSavingPaper"
      @close="closePaperModal"
      @submit="handlePaperSubmit"
    />

    <TagModal
      :open="isTagModalOpen"
      :is-saving="isSavingTag"
      @close="closeTagModal"
      @submit="handleCreateTag"
    />

    <ConfirmDialog
      :open="confirmDialog.open"
      :title="confirmDialog.title"
      :points="confirmDialog.points"
      :confirm-label="confirmDialog.confirmLabel"
      :is-loading="isDeleting"
      cancel-label="Keep it"
      @cancel="closeConfirmDialog"
      @confirm="handleConfirmDelete"
    />
  </main>
</template>
