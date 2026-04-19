<template>
  <article class="w-52 overflow-hidden border border-[var(--ink-black)] bg-[var(--white-soft)] p-3 shadow-sm">
    <div class="relative border border-[var(--white)] h-40 overflow-hidden" :style="coverStyle">
      <img
        v-if="song.cover_image"
        :src="song.cover_image"
        alt=""
        class="absolute inset-0 h-full w-full object-cover"
      />
      <div v-else class="flex h-full items-center justify-center">
        <Music4 class="h-9 w-9" :class="song.cover_color ? 'text-white/60' : 'text-[var(--white)]/85'" />
      </div>
      <!-- Play/Pause -->
      <button
        class="absolute bottom-3 right-3 flex h-10 w-10 items-center justify-center border border-[var(--ink-black)]/10 bg-white shadow-sm"
        @click="$emit('play', song)"
      >
        <Pause v-if="activeSongId === song.id && isPlaying" class="h-5 w-5 text-[var(--ink-black)]" />
        <Play v-else class="h-5 w-5 text-[var(--ink-black)]" />
      </button>
    </div>

    <div class="space-y-1.5 px-1 pt-3">
      <div class="flex items-center gap-1.5">
        <h3 class="line-clamp-1 text-[14px] leading-none font-semibold tracking-tight text-[var(--ink-black)] uppercase">
          {{ song.title || 'Title' }}
        </h3>
        <Globe v-if="song.privacy_level === 'PUBLIC'" class="h-3.5 w-3.5 shrink-0 text-[var(--ink-black)]/60" />
        <GlobeLock v-else class="h-3.5 w-3.5 shrink-0 text-[var(--ink-black)]/60" />
      </div>

      <div class="text-[11px] leading-tight font-semibold text-[var(--brand-yellow)]">
        #{{ song.genre || 'TAG' }} #{{ song.tone || 'TAG' }}
      </div>

      <div class="flex justify-end gap-1 pt-1">
        <button class="p-1" @click="$emit('edit', song)" title="Edit">
          <Pencil class="h-3.5 w-3.5 text-[var(--ink-black)]/60" />
        </button>
        <button class="p-1" @click="$emit('delete', song)" title="Delete">
          <Trash2 class="h-3.5 w-3.5 text-[var(--ink-black)]/60" />
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