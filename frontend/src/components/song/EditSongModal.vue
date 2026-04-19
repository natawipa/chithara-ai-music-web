<template>
  <Modal @close="$emit('close')">
    <div class="space-y-5 p-6">
      <div class="flex items-center justify-between border-b border-black/10 pb-4">
        <h3 class="text-xl font-semibold">Edit Song</h3>
        <button class="rounded-lg p-2 hover:bg-black/5" @click="$emit('close')">
          <X class="h-5 w-5" />
        </button>
      </div>

      <!-- Cover image section -->
      <div class="grid gap-2 text-sm font-medium">
        Cover Image
        <div class="flex items-center gap-4">
          <!-- Preview -->
          <div
            class="h-20 w-20 shrink-0 overflow-hidden border border-black/15"
            :style="previewStyle"
          >
            <img
              v-if="coverPreviewUrl || song.cover_image"
              :src="coverPreviewUrl || song.cover_image"
              class="h-full w-full object-cover"
              alt="Cover preview"
            />
            <div v-else class="flex h-full items-center justify-center">
              <Music4 class="h-6 w-6 text-white/70" />
            </div>
          </div>

          <!-- Upload / replace cover image -->
          <div class="flex flex-col gap-1.5">
            <label class="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-black/15 bg-white px-3 py-2 text-sm font-semibold hover:bg-black/5">
              <ImagePlus class="h-4 w-4" />
              {{ coverFile ? 'Change' : song.cover_image ? 'Replace image' : 'Upload image' }}
              <input type="file" accept="image/*" class="hidden" @change="onCoverFileChange" />
            </label>
            <span v-if="coverFile" class="max-w-[160px] truncate text-xs text-neutral-500">
              {{ coverFile.name }}
            </span>
          </div>
        </div>
      </div>

      <label class="grid gap-2 text-sm font-medium">
        Title
        <input v-model="form.title" type="text" class="rounded-xl border border-black/15 bg-white/60 px-3 py-2" />
      </label>

      <label class="grid gap-2 text-sm font-medium">
        Description
        <textarea v-model="form.description" rows="4" class="rounded-xl border border-black/15 bg-white/60 px-3 py-2" />
      </label>

      <div v-if="error" class="rounded-xl border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
        {{ error }}
      </div>

      <div class="flex items-center justify-end gap-3 border-t border-black/10 pt-4">
        <button class="rounded-xl border border-black/15 bg-white px-4 py-2 text-sm font-semibold" @click="$emit('close')">
          Cancel
        </button>
        <button
          class="inline-flex items-center gap-2 rounded-xl bg-neutral-900 px-4 py-2 text-sm font-semibold text-white hover:bg-neutral-800 disabled:opacity-60"
          @click="save"
          :disabled="saving"
        >
          <Save class="h-4 w-4" />
          {{ saving ? 'Saving…' : 'Save' }}
        </button>
      </div>
    </div>
  </Modal>
</template>

<script>
import { ImagePlus, Music4, Save, X } from 'lucide-vue-next'
import Modal from '../ui/Modal.vue'
import { updateSong, uploadCoverImage } from '../../api/song'

export default {
  name: 'EditSongModal',
  components: { Modal, ImagePlus, Music4, Save, X },
  props: {
    song: {
      type: Object,
      required: true,
    },
  },
  emits: ['close', 'saved'],
  data() {
    return {
      saving: false,
      error: '',
      coverFile: null,
      coverPreviewUrl: null,
      form: {
        title: this.song?.title || '',
        description: this.song?.description || '',
      },
    }
  },
  computed: {
    previewStyle() {
      if (this.coverPreviewUrl || this.song.cover_image) return {}
      return { backgroundColor: this.song.cover_color || 'var(--brand-yellow)' }
    },
  },
  methods: {
    onCoverFileChange(event) {
      const file = event.target.files?.[0]
      if (!file) return
      this.coverFile = file
      this.coverPreviewUrl = URL.createObjectURL(file)
    },
    async save() {
      this.error = ''
      this.saving = true
      try {
        let updatedSong = { ...this.song }

        if (this.coverFile) {
          const coverResult = await uploadCoverImage(this.song.id, this.coverFile)
          updatedSong.cover_image = coverResult.cover_image
          updatedSong.cover_color = coverResult.cover_color
        }

        const metaResult = await updateSong(this.song.id, {
          title: this.form.title,
          description: this.form.description,
        })

        this.$emit('saved', { ...updatedSong, ...metaResult })
      } catch (err) {
        this.error = err?.response?.data?.error || 'Failed to save.'
      } finally {
        this.saving = false
      }
    },
  },
  beforeUnmount() {
    if (this.coverPreviewUrl) URL.revokeObjectURL(this.coverPreviewUrl)
  },
}
</script>