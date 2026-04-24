<template>
  <article class="w-52 overflow-hidden rounded-xl bg-white p-3 shadow-sm">
    <div
      class="relative h-40 overflow-hidden rounded-xl"
      :style="coverStyle"
    >
      <img
        v-if="song.cover_image"
        :src="song.cover_image"
        alt=""
        class="absolute inset-0 h-full w-full object-cover"
      />

      <div v-else class="flex h-full items-center justify-center">
        <Music4 class="h-9 w-9 text-white/70" />
      </div>

      <!-- Play Button -->
      <button
        class="absolute bottom-3 right-3 flex h-11 w-11 items-center justify-center rounded-xl bg-white shadow-md"
        @click="$emit('play', song)"
      >
        <Pause
          v-if="activeSongId === song.id && isPlaying"
          class="h-5 w-5 text-black"
        />
        <Play
          v-else
          fill="black"
          class="h-5 w-5 text-black ml-0.5"
        />
      </button>
    </div>

    <div class="space-y-1.5 px-1 pt-3">
      <div class="flex items-center gap-1.5">
        <h3 class="line-clamp-1 text-sm font-semibold uppercase text-black">
          {{ song.title || 'Title' }}
        </h3>

        <Globe
          v-if="song.privacy_level === 'PUBLIC'"
          class="h-3.5 w-3.5 text-black/50"
        />
        <GlobeLock
          v-else
          class="h-3.5 w-3.5 text-black/50"
        />
      </div>

      <div class="text-[11px] font-semibold text-[var(--brand-yellow)]">
        #{{ song.genre || 'TAG' }} #{{ song.tone || 'TAG' }}
      </div>

      <div class="flex justify-end gap-2 pt-1">
        <button @click="$emit('edit', song)">
          <Pencil class="h-4 w-4 text-black/60" />
        </button>

        <button @click="$emit('delete', song)">
          <Trash2 class="h-4 w-4 text-black/60" />
        </button>
      </div>
    </div>
  </article>
</template>

<script>
import { Globe, GlobeLock, Music4, Pause, Pencil, Play, Trash2 } from 'lucide-vue-next'

export default {
  name: 'SongCard',
  components: { Globe, GlobeLock, Music4, Pause, Pencil, Play, Trash2 },
  props: {
    song: {
      type: Object,
      required: true,
    },
    activeSongId: {
      type: [Number, String, null],
      default: null,
    },
    isPlaying: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['play', 'edit', 'delete'],
  computed: {
    coverStyle() {
      if (this.song.cover_image) return {}
      return { backgroundColor: this.song.cover_color || 'var(--brand-yellow)' }
    },
  },
}
</script>