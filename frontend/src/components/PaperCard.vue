<script setup lang="ts">
import {
  BookMarked,
  CheckCircle2,
  CircleDot,
  Clock3,
  Code2,
  Trash2,
  Edit3,
  ExternalLink,
  FileText,
  Star,
} from 'lucide-vue-next'
import type { Paper, PaperStatus } from '../types'

const props = defineProps<{
  paper: Paper
}>()

const emit = defineEmits<{
  edit: [paper: Paper]
  delete: [paperId: number]
  statusChange: [paperId: number, status: PaperStatus]
}>()

const statusOptions: Array<{ label: string; value: PaperStatus; icon: typeof Clock3 }> = [
  { label: 'ToRead', value: 'to_read', icon: Clock3 },
  { label: 'Reading', value: 'reading', icon: CircleDot },
  { label: 'Completed', value: 'completed', icon: CheckCircle2 },
]

function statusClass(status: PaperStatus) {
  if (status === 'completed') {
    return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  }

  if (status === 'reading') {
    return 'border-amber-200 bg-amber-50 text-amber-700'
  }

  return 'border-sky-200 bg-sky-50 text-sky-700'
}

function statusLabel(status: PaperStatus) {
  if (status === 'to_read') {
    return 'ToRead'
  }

  if (status === 'reading') {
    return 'Reading'
  }

  return 'Completed'
}

</script>

<template>
  <article
    class="group rounded-[1.75rem] border border-stone-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-stone-300 hover:shadow-[0_20px_60px_rgba(64,52,38,0.10)]"
  >
    <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <span
            class="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold"
            :class="statusClass(props.paper.status)"
          >
            <BookMarked class="size-3.5" />
            {{ statusLabel(props.paper.status) }}
          </span>
          <span class="inline-flex items-center gap-1 rounded-full bg-stone-100 px-2.5 py-1 text-xs font-medium text-stone-600">
            <Star class="size-3.5 fill-current" />
            {{ props.paper.priority }}
          </span>
          <span v-if="props.paper.venue || props.paper.pub_year" class="text-xs font-medium text-stone-400">
            {{ [props.paper.venue, props.paper.pub_year].filter(Boolean).join(' · ') }}
          </span>
        </div>

        <h3 class="mt-4 text-xl font-semibold leading-tight tracking-[-0.03em] text-slate-950">
          {{ props.paper.aka_name || props.paper.title }}
        </h3>
        <p
          v-if="props.paper.aka_name"
          class="mt-1 line-clamp-2 text-sm leading-6 text-stone-500"
        >
          {{ props.paper.title }}
        </p>
        <p v-if="props.paper.authors_display" class="mt-3 text-sm text-stone-500">
          {{ props.paper.authors_display }}
        </p>
      </div>

      <div class="flex shrink-0 flex-wrap gap-2">
        <button
          v-for="option in statusOptions"
          :key="option.value"
          type="button"
          class="inline-flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition"
          :class="
            props.paper.status === option.value
              ? 'border-slate-950 bg-slate-950 text-stone-50'
              : 'border-stone-200 bg-white text-stone-500 hover:border-stone-300 hover:text-slate-950'
          "
          @click="emit('statusChange', props.paper.id, option.value)"
        >
          <component :is="option.icon" class="size-3.5" />
          {{ option.label }}
        </button>
      </div>
    </div>

    <div class="mt-5 flex flex-wrap items-center gap-2">
      <span
        v-for="tag in props.paper.tags"
        :key="tag.id"
        class="inline-flex items-center gap-2 rounded-full border border-stone-200 bg-stone-50 px-3 py-1.5 text-xs font-semibold text-stone-600"
      >
        {{ tag.name }}
      </span>
      <span v-if="props.paper.tags.length === 0" class="text-xs text-stone-400">No tags</span>
    </div>

    <div class="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-stone-100 pt-4">
      <div class="flex flex-wrap items-center gap-2">
        <a
          v-if="props.paper.pdf_url || props.paper.pdf_path"
          :href="props.paper.pdf_url || props.paper.pdf_path || undefined"
          target="_blank"
          rel="noreferrer"
          class="inline-flex items-center gap-1.5 rounded-xl bg-stone-100 px-3 py-2 text-xs font-semibold text-stone-600 transition hover:bg-stone-200 hover:text-slate-950"
        >
          <FileText class="size-3.5" />
          PDF
          <ExternalLink class="size-3" />
        </a>
        <a
          v-if="props.paper.code_url"
          :href="props.paper.code_url"
          target="_blank"
          rel="noreferrer"
          class="inline-flex items-center gap-1.5 rounded-xl bg-stone-100 px-3 py-2 text-xs font-semibold text-stone-600 transition hover:bg-stone-200 hover:text-slate-950"
        >
          <Code2 class="size-3.5" />
          Code
          <ExternalLink class="size-3" />
        </a>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="inline-flex items-center gap-1.5 rounded-xl px-3 py-2 text-xs font-semibold text-stone-500 transition hover:bg-stone-100 hover:text-slate-950"
          @click="emit('edit', props.paper)"
        >
          <Edit3 class="size-3.5" />
          Edit
        </button>
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-xl p-2 text-red-500 transition hover:bg-red-50 hover:text-red-700"
          title="Delete paper"
          @click="emit('delete', props.paper.id)"
        >
          <Trash2 class="size-4" />
        </button>
      </div>
    </div>
  </article>
</template>
