<script setup lang="ts">
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-vue-next'
import PaperCard from './PaperCard.vue'
import type { PaginationMeta, Paper, PaperStatus } from '../types'

defineProps<{
  papers: Paper[]
  meta: PaginationMeta
  isLoading: boolean
}>()

const emit = defineEmits<{
  edit: [paper: Paper]
  delete: [paperId: number]
  statusChange: [paperId: number, status: PaperStatus]
  pageChange: [page: number]
}>()
</script>

<template>
  <section class="space-y-4">
    <div v-if="isLoading" class="grid gap-4">
      <div
        v-for="index in 3"
        :key="index"
        class="h-44 animate-pulse rounded-[1.75rem] border border-stone-200 bg-white/70"
      />
    </div>

    <template v-else>
      <div v-if="papers.length > 0" class="grid gap-4">
        <PaperCard
          v-for="paper in papers"
          :key="paper.id"
          :paper="paper"
          @edit="emit('edit', $event)"
          @delete="emit('delete', $event)"
          @status-change="(paperId, status) => emit('statusChange', paperId, status)"
        />
      </div>

      <div
        v-else
        class="rounded-[1.75rem] border border-stone-200 bg-white px-6 py-16 text-center shadow-sm"
      >
        <Loader2 class="mx-auto mb-4 size-6 text-stone-300" />
        <h3 class="text-lg font-semibold text-slate-950">No papers found</h3>
        <p class="mt-2 text-sm text-stone-500">
          Try clearing filters, seeding the backend, or creating a new paper.
        </p>
      </div>
    </template>

    <footer
      class="flex flex-col gap-3 rounded-[1.5rem] border border-stone-200 bg-white px-4 py-3 text-sm text-stone-500 shadow-sm sm:flex-row sm:items-center sm:justify-between"
    >
      <span>
        Page {{ meta.page || 1 }} of {{ meta.total_pages || 0 }} · {{ meta.total }} papers
      </span>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 font-medium transition hover:border-stone-300 hover:text-slate-950 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="meta.page <= 1 || isLoading"
          @click="emit('pageChange', meta.page - 1)"
        >
          <ChevronLeft class="size-4" />
          Previous
        </button>
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 font-medium transition hover:border-stone-300 hover:text-slate-950 disabled:cursor-not-allowed disabled:opacity-40"
          :disabled="meta.total_pages === 0 || meta.page >= meta.total_pages || isLoading"
          @click="emit('pageChange', meta.page + 1)"
        >
          Next
          <ChevronRight class="size-4" />
        </button>
      </div>
    </footer>
  </section>
</template>
