<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { CheckCircle2, Loader2, Sparkles, X } from 'lucide-vue-next'
import { usePaperStore } from '../stores/paper'
import type { Paper, PaperCreatePayload, PaperStatus, PaperUpdatePayload, Tag } from '../types'

const props = defineProps<{
  open: boolean
  paper: Paper | null
  tags: Tag[]
  isSaving: boolean
}>()

const emit = defineEmits<{
  close: []
  submit: [payload: PaperCreatePayload | PaperUpdatePayload, paperId?: number]
}>()

const paperStore = usePaperStore()
const { parseTask, isStartingParseTask, isPollingParseTask, parseTaskMessage } =
  storeToRefs(paperStore)
const importUrl = ref('')
const showParseSuccessToast = ref(false)

const form = reactive({
  title: '',
  aka_name: '',
  authors_display: '',
  venue: '',
  pub_year: '',
  priority: 3,
  status: 'to_read' as PaperStatus,
  pdf_url: '',
  code_url: '',
  tag_ids: [] as number[],
})

const isEditing = computed(() => props.paper !== null)
const canSubmit = computed(() => form.title.trim().length > 0 && !props.isSaving)
const isParsing = computed(() => isStartingParseTask.value || isPollingParseTask.value)
const parseProgress = computed(() => parseTask.value?.progress ?? 0)

watch(
  () => [props.open, props.paper] as const,
  () => {
    if (!props.open) {
      return
    }

    showParseSuccessToast.value = false
    importUrl.value = ''
    form.title = props.paper?.title ?? ''
    form.aka_name = props.paper?.aka_name ?? ''
    form.authors_display = props.paper?.authors_display ?? ''
    form.venue = props.paper?.venue ?? ''
    form.pub_year = props.paper?.pub_year?.toString() ?? ''
    form.priority = props.paper?.priority ?? 3
    form.status = props.paper?.status ?? 'to_read'
    form.pdf_url = props.paper?.pdf_url ?? ''
    form.code_url = props.paper?.code_url ?? ''
    form.tag_ids = props.paper?.tags.map((tag) => tag.id) ?? []

    if (!props.paper) {
      paperStore.resetParseTask()
    }
  },
  { immediate: true },
)

watch(
  () => parseTask.value?.status,
  (status) => {
    if (status !== 'completed' || !parseTask.value?.result || isEditing.value) {
      return
    }

    const draft = parseTask.value.result
    form.title = draft.title ?? ''
    form.authors_display = draft.authors_display || draft.authors || ''
    form.venue = draft.venue ?? ''
    form.pub_year = draft.pub_year?.toString() ?? draft.year?.toString() ?? ''
    form.priority = draft.priority ?? 3
    form.status = draft.status ?? 'to_read'
    form.pdf_url = draft.pdf_url || draft.pdf_path || ''
    showParseSuccessToast.value = true
  },
)

function toggleTag(tagId: number) {
  if (form.tag_ids.includes(tagId)) {
    form.tag_ids = form.tag_ids.filter((id) => id !== tagId)
    return
  }

  form.tag_ids = [...form.tag_ids, tagId]
}

function emptyToNull(value: string) {
  const trimmed = value.trim()
  return trimmed.length > 0 ? trimmed : null
}

function handleSubmit() {
  if (!canSubmit.value) {
    return
  }

  const payload: PaperCreatePayload | PaperUpdatePayload = {
    title: form.title.trim(),
    aka_name: emptyToNull(form.aka_name),
    authors_display: emptyToNull(form.authors_display),
    venue: emptyToNull(form.venue),
    pub_year: form.pub_year ? Number(form.pub_year) : null,
    priority: form.priority,
    status: form.status,
    pdf_url: emptyToNull(form.pdf_url),
    code_url: emptyToNull(form.code_url),
    tag_ids: form.tag_ids,
  }

  emit('submit', payload, props.paper?.id)
}

async function handleParseUrl() {
  const url = importUrl.value.trim()
  if (!url || isParsing.value) {
    return
  }

  showParseSuccessToast.value = false
  await paperStore.startParseTask(url)
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/35 px-4 py-6 backdrop-blur-sm"
      @click.self="emit('close')"
    >
      <form
        class="max-h-[92vh] w-full max-w-3xl overflow-y-auto rounded-[2rem] border border-stone-200 bg-[#fffdf8] p-6 shadow-[0_30px_100px_rgba(15,23,42,0.28)]"
        @submit.prevent="handleSubmit"
      >
        <header class="flex items-start justify-between gap-4 border-b border-stone-200 pb-5">
          <div>
            <p class="text-sm font-medium text-stone-500">
              {{ isEditing ? 'Edit existing paper' : 'Create new paper' }}
            </p>
            <h2 class="mt-1 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
              {{ isEditing ? 'Update paper details' : 'Add paper to library' }}
            </h2>
          </div>
          <button
            type="button"
            class="rounded-2xl p-2 text-stone-400 transition hover:bg-stone-100 hover:text-slate-950"
            @click="emit('close')"
          >
            <X class="size-5" />
          </button>
        </header>

        <section
          v-if="!isEditing"
          class="mt-6 rounded-[1.5rem] border border-stone-200 bg-stone-50/70 p-4"
        >
          <div class="flex items-center gap-2 text-sm font-semibold text-stone-600">
            <Sparkles class="size-4 text-slate-500" />
            URL Import
          </div>
          <div class="mt-3 flex flex-col gap-3 md:flex-row">
            <input
              v-model="importUrl"
              type="text"
              placeholder="输入 ArXiv 链接或 DOI"
              class="min-w-0 flex-1 rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
            />
            <button
              type="button"
              class="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-stone-50 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="!importUrl.trim() || isParsing"
              @click="handleParseUrl"
            >
              <Loader2 v-if="isParsing" class="size-4 animate-spin" />
              解析并填充
            </button>
          </div>

          <div v-if="parseTaskMessage || parseTask" class="mt-4">
            <div class="flex items-center justify-between text-xs font-medium text-stone-500">
              <span>{{ parseTaskMessage ?? '等待解析任务...' }}</span>
              <span>{{ parseProgress }}%</span>
            </div>
            <div class="mt-2 h-2 overflow-hidden rounded-full bg-stone-200">
              <div
                class="h-full rounded-full bg-slate-950 transition-all duration-500"
                :style="{ width: `${parseProgress}%` }"
              />
            </div>
            <p v-if="parseTask?.status === 'failed'" class="mt-2 text-sm font-medium text-red-600">
              {{ parseTask.error_msg }}
            </p>
          </div>

          <div
            v-if="showParseSuccessToast"
            class="mt-4 flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
          >
            <CheckCircle2 class="mt-0.5 size-4 shrink-0" />
            <span>解析成功，请补充别名(AKA)和标签后确认保存</span>
          </div>
        </section>

        <div class="mt-6 grid gap-4 md:grid-cols-2">
          <label class="md:col-span-2">
            <span class="text-sm font-semibold text-stone-600">Title *</span>
            <input
              v-model="form.title"
              required
              type="text"
              class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
              placeholder="Attention Is All You Need"
            />
          </label>

          <label>
            <span class="text-sm font-semibold text-stone-600">AKA</span>
            <input
              v-model="form.aka_name"
              type="text"
              class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
              placeholder="Transformer"
            />
          </label>

          <label>
            <span class="text-sm font-semibold text-stone-600">Authors</span>
            <input
              v-model="form.authors_display"
              type="text"
              class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
              placeholder="Vaswani et al."
            />
          </label>

          <label>
            <span class="text-sm font-semibold text-stone-600">Venue</span>
            <input
              v-model="form.venue"
              type="text"
              class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
              placeholder="NeurIPS"
            />
          </label>

          <label>
            <span class="text-sm font-semibold text-stone-600">Year</span>
            <input
              v-model="form.pub_year"
              type="number"
              min="1900"
              max="3000"
              class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
              placeholder="2017"
            />
          </label>

          <label>
            <span class="text-sm font-semibold text-stone-600">Priority</span>
            <select
              v-model.number="form.priority"
              class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
            >
              <option v-for="value in [1, 2, 3, 4, 5]" :key="value" :value="value">
                {{ value }} star{{ value > 1 ? 's' : '' }}
              </option>
            </select>
          </label>

          <label>
            <span class="text-sm font-semibold text-stone-600">Status</span>
            <select
              v-model="form.status"
              class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
            >
              <option value="to_read">ToRead</option>
              <option value="reading">Reading</option>
              <option value="completed">Completed</option>
            </select>
          </label>

          <label>
            <span class="text-sm font-semibold text-stone-600">PDF Link</span>
            <input
              v-model="form.pdf_url"
              type="url"
              class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
              placeholder="https://arxiv.org/abs/..."
            />
          </label>

          <label>
            <span class="text-sm font-semibold text-stone-600">Code Link</span>
            <input
              v-model="form.code_url"
              type="url"
              class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
              placeholder="https://github.com/..."
            />
          </label>
        </div>

        <section class="mt-6">
          <p class="text-sm font-semibold text-stone-600">Tags</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <button
              v-for="tag in tags"
              :key="tag.id"
              type="button"
              class="inline-flex items-center gap-2 rounded-full border px-3 py-2 text-xs font-semibold transition"
              :class="
                form.tag_ids.includes(tag.id)
                  ? 'border-slate-950 bg-slate-950 text-stone-50'
                  : 'border-stone-200 bg-white text-stone-600 hover:border-stone-300 hover:text-slate-950'
              "
              @click="toggleTag(tag.id)"
            >
              <span class="size-2 rounded-full" :style="{ backgroundColor: tag.color ?? '#a8a29e' }" />
              {{ tag.name }}
            </button>
          </div>
        </section>

        <footer class="mt-8 flex flex-col-reverse gap-3 border-t border-stone-200 pt-5 sm:flex-row sm:justify-end">
          <button
            type="button"
            class="rounded-2xl border border-stone-200 bg-white px-5 py-3 text-sm font-semibold text-stone-600 transition hover:border-stone-300 hover:text-slate-950"
            @click="emit('close')"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-stone-50 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!canSubmit"
          >
            <Loader2 v-if="isSaving" class="size-4 animate-spin" />
            {{ isEditing ? 'Save changes' : '保存到我的文献库' }}
          </button>
        </footer>
      </form>
    </div>
  </Teleport>
</template>
