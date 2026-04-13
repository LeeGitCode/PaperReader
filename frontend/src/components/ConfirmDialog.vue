<script setup lang="ts">
import { AlertTriangle, Loader2, X } from 'lucide-vue-next'

defineProps<{
  open: boolean
  title: string
  message?: string
  points?: string[]
  confirmLabel?: string
  cancelLabel?: string
  isLoading?: boolean
}>()

const emit = defineEmits<{
  cancel: []
  confirm: []
}>()
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/40 px-4 py-6 backdrop-blur-sm"
      @click.self="emit('cancel')"
    >
      <section
        class="w-full max-w-md rounded-[2rem] border border-red-100 bg-[#fffdf8] p-6 shadow-[0_30px_100px_rgba(127,29,29,0.24)]"
      >
        <header class="flex items-start gap-4">
          <div class="grid size-12 shrink-0 place-items-center rounded-2xl bg-red-50 text-red-600">
            <AlertTriangle class="size-6" />
          </div>
          <div class="min-w-0 flex-1">
            <h2 class="text-xl font-semibold tracking-[-0.03em] text-slate-950">{{ title }}</h2>
            <p v-if="message" class="mt-2 text-sm leading-6 text-stone-600">{{ message }}</p>
            <ul v-if="points?.length" class="mt-3 space-y-2 text-sm leading-6 text-stone-600">
              <li v-for="point in points" :key="point" class="flex gap-2">
                <span class="mt-2 size-1.5 shrink-0 rounded-full bg-red-400" />
                <span>{{ point }}</span>
              </li>
            </ul>
          </div>
          <button
            type="button"
            class="rounded-xl p-2 text-stone-400 transition hover:bg-stone-100 hover:text-slate-950"
            :disabled="isLoading"
            @click="emit('cancel')"
          >
            <X class="size-4" />
          </button>
        </header>

        <footer class="mt-7 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            class="rounded-2xl border border-stone-200 bg-white px-5 py-3 text-sm font-semibold text-stone-600 transition hover:border-stone-300 hover:text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="isLoading"
            @click="emit('cancel')"
          >
            {{ cancelLabel ?? 'Cancel' }}
          </button>
          <button
            type="button"
            class="inline-flex items-center justify-center gap-2 rounded-2xl bg-red-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-red-600/20 transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="isLoading"
            @click="emit('confirm')"
          >
            <Loader2 v-if="isLoading" class="size-4 animate-spin" />
            {{ confirmLabel ?? 'Delete' }}
          </button>
        </footer>
      </section>
    </div>
  </Teleport>
</template>
