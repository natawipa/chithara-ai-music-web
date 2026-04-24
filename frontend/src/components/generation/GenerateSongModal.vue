<template>
  <Modal @close="$emit('close')">
    <div class="space-y-5 p-6">
      <div class="flex items-center justify-between border-b border-black/10 pb-4">
        <h3 class="text-2xl font-semibold text-neutral-900">
          Generate Song
        </h3>

        <button
          class="rounded-lg p-2 hover:bg-black/5"
          @click="$emit('close')"
        >
          <X class="h-5 w-5" />
        </button>
      </div>

      <div class="grid gap-4">

        <label class="grid gap-2 text-sm font-medium">
          Title
          <input
            v-model="form.title"
            type="text"
            placeholder="Sunset Memories"
            class="rounded-xl border border-black/15 bg-white/60 px-3 py-2"
          />
        </label>

        <label class="grid gap-2 text-sm font-medium">
          Description
          <textarea
            v-model="form.description"
            rows="4"
            placeholder="Describe the mood, story, or style..."
            class="rounded-xl border border-black/15 bg-white/60 px-3 py-2"
          />
        </label>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">

          <!-- Genre -->
          <div class="grid gap-2 text-sm font-medium">
            <label>Genre</label>

            <div class="relative">
              <select
                v-model="form.genre"
                class="modal-select w-full rounded-xl border border-black/15 bg-white/60 px-3 py-2 pr-10"
              >
                <option value="">Select genre</option>
                <option
                  v-for="genre in genreOptions"
                  :key="genre.value"
                  :value="genre.value"
                >
                  {{ genre.label }}
                </option>
              </select>

              <ChevronDown
                class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-black/50"
              />
            </div>
          </div>

          <!-- Tone -->
          <div class="grid gap-2 text-sm font-medium">
            <label>Tone</label>

            <div class="relative">
              <select
                v-model="form.tone"
                class="modal-select w-full rounded-xl border border-black/15 bg-white/60 px-3 py-2 pr-10"
              >
                <option value="">Select tone</option>
                <option
                  v-for="tone in toneOptions"
                  :key="tone.value"
                  :value="tone.value"
                >
                  {{ tone.label }}
                </option>
              </select>

              <ChevronDown
                class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-black/50"
              />
            </div>
          </div>

        </div>

        <!-- Occasion -->
        <div class="grid gap-2 text-sm font-medium">
          <label>Occasion (optional)</label>

          <div class="relative">
            <select
              v-model="form.occasion"
              class="modal-select w-full rounded-xl border border-black/15 bg-white/60 px-3 py-2 pr-10"
            >
              <option value="">None</option>

              <option
                v-for="occasion in occasionOptions"
                :key="occasion.value"
                :value="occasion.value"
              >
                {{ occasion.label }}
              </option>
            </select>

            <ChevronDown
              class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-black/50"
            />
          </div>
        </div>

        <div
          v-if="error"
          class="rounded-xl border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {{ error }}
        </div>

      </div>

      <div class="flex items-center justify-end gap-3 border-t border-black/10 pt-4">
        <button
          class="rounded-xl border border-black/15 bg-white px-4 py-2 text-sm font-semibold"
          @click="$emit('close')"
        >
          Cancel
        </button>

        <button
          class="inline-flex items-center gap-2 rounded-xl bg-amber-400/75 px-4 py-2 text-sm font-semibold text-neutral-900 hover:bg-amber-300/75 disabled:opacity-60"
          @click="submit"
          :disabled="submitting"
        >
          Generate
        </button>
      </div>

    </div>
  </Modal>
</template>

<script>
import Modal from '../ui/Modal.vue'
import { createGeneration } from '../../api/generation'
import {
  GENRE_OPTIONS,
  OCCASION_OPTIONS,
  TONE_OPTIONS,
} from '../../constants/enums'

import {
  X,
  ChevronDown
} from 'lucide-vue-next'

export default {
  name: 'GenerateSongModal',

  components: {
    Modal,
    X,
    ChevronDown,
  },

  emits: ['close', 'generated'],

  data() {
    return {
      submitting: false,
      error: '',

      genreOptions: GENRE_OPTIONS,
      toneOptions: TONE_OPTIONS,
      occasionOptions: OCCASION_OPTIONS,

      form: {
        title: '',
        description: '',
        genre: '',
        tone: '',
        occasion: '',
      },
    }
  },

  methods: {
    async submit() {
      this.error = ''

      if (
        !this.form.title ||
        !this.form.description ||
        !this.form.genre ||
        !this.form.tone
      ) {
        this.error =
          'Title, description, genre, and tone are required.'
        return
      }

      this.submitting = true

      try {
        const generation = await createGeneration({
          ...this.form
        })

        this.$emit('generated', generation)

      } catch (err) {
        this.error =
          err?.response?.data?.error ||
          'Failed to create generation.'

      } finally {
        this.submitting = false
      }
    },
  },
}
</script>

<style scoped>
label {
  display: flex;
  flex-direction: column;
  margin: 8px;
}

.modal-select {
  appearance: none;
  -webkit-appearance: none;
}
</style>