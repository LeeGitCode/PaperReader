<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Loader2, Plus, X } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  isSaving: boolean
}>()

const emit = defineEmits<{
  close: []
  submit: [name: string]
}>()

const tagName = ref('')
const canSubmit = computed(() => tagName.value.trim().length > 0 && !props.isSaving)

watch(
  () => props.open,
  (open) => {
    if (open) {
      tagName.value = ''
    }
  },
)

function handleSubmit() {
  if (!canSubmit.value) {
    return
  }

  emit('submit', tagName.value.trim())
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
        class="w-full max-w-md rounded-[2rem] border border-stone-200 bg-[#fffdf8] p-6 shadow-[0_30px_100px_rgba(64,52,38,0.20)]"
        @submit.prevent="handleSubmit"
      >
        <header class="flex items-start justify-between gap-4">
          <div class="flex items-start gap-4">
            <div class="grid size-12 shrink-0 place-items-center rounded-2xl bg-slate-950 text-stone-50">
              <Plus class="size-5" />
            </div>
            <div>
              <p class="text-sm font-medium text-stone-500">New research tag</p>
              <h2 class="mt-1 text-xl font-semibold tracking-[-0.03em] text-slate-950">Create Tag</h2>
            </div>
          </div>
          <button
            type="button"
            class="rounded-xl p-2 text-stone-400 transition hover:bg-stone-100 hover:text-slate-950"
            :disabled="isSaving"
            @click="emit('close')"
          >
            <X class="size-4" />
          </button>
        </header>

        <label class="mt-6 block">
          <span class="text-sm font-semibold text-stone-600">Tag name</span>
          <input
            v-model="tagName"
            autofocus
            type="text"
            placeholder="Distributed Training"
            class="mt-2 w-full rounded-2xl border border-stone-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-slate-400"
          />
        </label>

        <p class="mt-3 text-sm leading-6 text-stone-500">
          Color will be assigned automatically by the backend.
        </p>

        <footer class="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            class="rounded-2xl border border-stone-200 bg-white px-5 py-3 text-sm font-semibold text-stone-600 transition hover:border-stone-300 hover:text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="isSaving"
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
            Create
          </button>
        </footer>
      </form>
    </div>
  </Teleport>
</template>
