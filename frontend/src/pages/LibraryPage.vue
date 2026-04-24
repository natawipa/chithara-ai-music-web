<template>
  <main class="min-h-screen pb-28">
    <UiNavbar :show-generate-button="true" :show-logout-button="true" @generate="showGenerate = true" />

    <section class="mx-auto max-w-7xl px-6 py-8">
      <div class="mb-6 flex flex-wrap gap-3">
        <div class="relative min-w-[220px] flex-1">
          <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--ink-black)]/60" />
          <input
            v-model="searchText"
            placeholder="Search songs..."
            class="w-full rounded-xl border border-[var(--ink-black)] bg-[var(--white)] py-2 pl-10 pr-3 text-sm"
          />
        </div>

        <div class="relative">
          <select v-model="genreFilter" class="filter-select rounded-xl border border-[var(--ink-black)] bg-[var(--white)] px-3 py-2 text-sm">
            <option value="">All genres</option>
            <option v-for="g in genres" :key="g" :value="g">{{ g }}</option>
          </select>
          <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--ink-black)]/70" />
        </div>

        <div class="relative">
          <select v-model="privacyFilter" class="filter-select rounded-xl border border-[var(--ink-black)] bg-[var(--white)] px-3 py-2 text-sm">
            <option value="">All</option>
            <option v-for="privacy in privacyLevelOptions" :key="privacy.value" :value="privacy.value">
              {{ privacy.label }}
            </option>
          </select>
          <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--ink-black)]/70" />
        </div>

        <div class="relative">
          <select v-model="sortBy" class="filter-select rounded-xl border border-[var(--ink-black)] bg-[var(--white)] px-3 py-2 text-sm">
            <option value="new">Newest first</option>
            <option value="old">Oldest first</option>
            <option value="title">Title A-Z</option>
          </select>
          <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--ink-black)]/70" />
        </div>
      </div>

      <div v-if="error" class="mb-4 rounded-xl border border-red-300 bg-red-50/70 px-4 py-3 text-sm text-red-800">
        {{ error }}
      </div>

      <div
        v-if="generationMessage"
        class="mb-4 rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900"
      >
        {{ generationMessage }}
      </div>

      <div v-if="loading" class="text-sm text-neutral-600">Loading songs...</div>

      <div v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
        <SongCard
          v-for="song in filteredSongs"
          :key="song.id"
          :song="song"
          :active-song-id="currentSong ? currentSong.id : null"
          :is-playing="isPlaying"
          @play="togglePlay"
          @download="downloadSong"
          @edit="openEdit"
          @delete="deleteSong"
        />
      </div>

      <p v-if="!loading && filteredSongs.length === 0" class="mt-4 text-sm text-neutral-600">
        No songs found.
      </p>
    </section>

    <GenerateSongModal
      v-if="showGenerate"
      @close="showGenerate = false"
      @generated="onGenerated"
    />

    <EditSongModal
      v-if="showEdit && selectedSong"
      :song="selectedSong"
      @close="closeEdit"
      @saved="onSongSaved"
    />

    <ShareSongModal
      v-if="showShare && selectedSong"
      :song="selectedSong"
      @close="closeShare"
    />

    <audio
      ref="audioPlayer"
      :src="currentSong ? songSource(currentSong) : ''"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @ended="onEnded"
      class="hidden"
    />

    <div
      v-if="currentSong"
      class="fixed bottom-0 left-0 right-0 border-t border-[var(--ink-black)] bg-[var(--white)] px-4 py-3"
    >
      <div class="mx-auto flex w-full max-w-7xl flex-col gap-2">
        <div class="flex items-center justify-between gap-4">
          <div class="min-w-0">
            <p class="truncate text-sm font-semibold text-neutral-900">{{ currentSong.title }}</p>
            <p class="text-xs text-neutral-600">{{ currentSong.genre }} · {{ currentSong.tone }}</p>
          </div>

          <div class="flex items-center gap-2">
            <button class="border border-transparent p-2 hover:border-[var(--ink-black)]" @click="playPrev">
              <SkipBack class="h-4 w-4" />
            </button>
            <button class="border border-transparent p-2 hover:border-[var(--ink-black)]" @click="toggleBottomPlay">
              <Pause v-if="isPlaying" class="h-4 w-4" />
              <Play v-else class="h-4 w-4" />
            </button>
            <button class="border border-transparent p-2 hover:border-[var(--ink-black)]" @click="playNext">
              <SkipForward class="h-4 w-4" />
            </button>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <span class="w-10 text-xs text-neutral-600">{{ formatTime(currentTime) }}</span>
          <input
            type="range"
            class="w-full"
            min="0"
            :max="duration || 0"
            :value="currentTime"
            @input="seek"
          />
          <span class="w-10 text-right text-xs text-neutral-600">{{ formatTime(duration) }}</span>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import { ChevronDown, Pause, Play, Search, SkipBack, SkipForward } from 'lucide-vue-next'
import SongCard from '../components/song/SongCard.vue'
import EditSongModal from '../components/song/EditSongModal.vue'
import ShareSongModal from '../components/song/ShareSongModal.vue'
import GenerateSongModal from '../components/generation/GenerateSongModal.vue'
import UiNavbar from '../components/ui/Navbar.vue'
import { PRIVACY_LEVEL_OPTIONS } from '../constants/enums'
import { getGenerationStatus } from '../api/generation'
import { deleteSongById, getLibrarySongs } from '../api/song'

export default {
  name: 'LibraryPage',
  components: {
    ChevronDown,
    Play,
    Pause,
    Search,
    SkipBack,
    SkipForward,
    SongCard,
    EditSongModal,
    ShareSongModal,
    GenerateSongModal,
    UiNavbar,
  },
  data() {
    return {
      songs: [],
      loading: false,
      error: '',
      showGenerate: false,
      showEdit: false,
      showShare: false,
      selectedSong: null,
      searchText: '',
      genreFilter: '',
      privacyFilter: '',
      privacyLevelOptions: PRIVACY_LEVEL_OPTIONS,
      sortBy: 'new',
      currentSong: null,
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      generationMessage: '',
      generationPollTimer: null,
      activeGenerationId: null,
    }
  },
  computed: {
    genres() {
      return [...new Set(this.songs.map((song) => song.genre).filter(Boolean))]
    },
    filteredSongs() {
      let list = [...this.songs]

      if (this.searchText.trim()) {
        const q = this.searchText.trim().toLowerCase()
        list = list.filter((song) => (song.title || '').toLowerCase().includes(q))
      }

      if (this.genreFilter) {
        list = list.filter((song) => song.genre === this.genreFilter)
      }

      if (this.privacyFilter) {
        list = list.filter((song) => song.privacy_level === this.privacyFilter)
      }

      if (this.sortBy === 'title') {
        list.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
      } else if (this.sortBy === 'old') {
        list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      } else {
        list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      }

      return list
    },
  },
  mounted() {
    this.loadSongs()
  },
  beforeUnmount() {
    const audio = this.$refs.audioPlayer
    if (audio) {
      audio.pause()
    }
    this.stopGenerationPolling()
  },
  methods: {
    stopGenerationPolling() {
      if (this.generationPollTimer) {
        clearTimeout(this.generationPollTimer)
        this.generationPollTimer = null
      }
    },
    scheduleGenerationPoll() {
      this.stopGenerationPolling()
      if (!this.activeGenerationId) return
      this.generationPollTimer = window.setTimeout(() => {
        this.pollGenerationStatus()
      }, 5000)
    },
    async pollGenerationStatus() {
      if (!this.activeGenerationId) return

      try {
        const status = await getGenerationStatus(this.activeGenerationId)
        if (status.status === 'COMPLETED') {
          this.generationMessage = 'Song generated successfully.'
          this.activeGenerationId = null
          this.stopGenerationPolling()
          await this.loadSongs()
          return
        }

        if (status.status === 'FAILED' || status.status === 'CANCELLED') {
          this.error = status.error || 'Song generation failed.'
          this.generationMessage = ''
          this.activeGenerationId = null
          this.stopGenerationPolling()
          return
        }

        this.generationMessage = 'Generating song... This page will update automatically.'
        this.scheduleGenerationPoll()
      } catch (err) {
        this.error = err?.response?.data?.error || 'Failed to refresh generation status.'
        this.generationMessage = ''
        this.activeGenerationId = null
        this.stopGenerationPolling()
      }
    },
    songSource(song) {
      return song?.audio_file || song?.audio_url || ''
    },
    async togglePlay(song) {
      const audio = this.$refs.audioPlayer
      if (!audio) return

      const src = this.songSource(song)
      if (!src) {
        this.error = 'This song has no playable audio URL.'
        return
      }

      if (this.currentSong && this.currentSong.id === song.id) {
        if (this.isPlaying) {
          audio.pause()
          this.isPlaying = false
        } else {
          try {
            await audio.play()
            this.isPlaying = true
          } catch (_) {
            this.error = 'Unable to start audio playback.'
          }
        }
        return
      }

      this.currentSong = song
      this.currentTime = 0
      this.duration = 0

      this.$nextTick(async () => {
        const player = this.$refs.audioPlayer
        if (!player) return
        try {
          await player.play()
          this.isPlaying = true
        } catch (_) {
          this.error = 'Unable to start audio playback.'
          this.isPlaying = false
        }
      })
    },
    async toggleBottomPlay() {
      if (!this.currentSong) return
      await this.togglePlay(this.currentSong)
    },
    onTimeUpdate(event) {
      this.currentTime = event.target.currentTime || 0
    },
    onLoadedMetadata(event) {
      this.duration = event.target.duration || 0
    },
    onEnded() {
      this.isPlaying = false
    },
    seek(event) {
      const player = this.$refs.audioPlayer
      if (!player) return
      const value = Number(event.target.value || 0)
      player.currentTime = value
      this.currentTime = value
    },
    formatTime(sec) {
      const value = Math.floor(sec || 0)
      const min = Math.floor(value / 60)
      const rem = value % 60
      return `${min}:${String(rem).padStart(2, '0')}`
    },
    playNext() {
      if (!this.currentSong || this.filteredSongs.length === 0) return
      const index = this.filteredSongs.findIndex((song) => song.id === this.currentSong.id)
      const next = this.filteredSongs[(index + 1) % this.filteredSongs.length]
      this.togglePlay(next)
    },
    playPrev() {
      if (!this.currentSong || this.filteredSongs.length === 0) return
      const index = this.filteredSongs.findIndex((song) => song.id === this.currentSong.id)
      const prev = this.filteredSongs[(index - 1 + this.filteredSongs.length) % this.filteredSongs.length]
      this.togglePlay(prev)
    },
    async loadSongs() {
      this.loading = true
      this.error = ''
      try {
        const data = await getLibrarySongs()
        this.songs = Array.isArray(data) ? data : (data.results || [])
      } catch (err) {
        this.error = err?.response?.data?.error || 'Failed to load songs.'
      } finally {
        this.loading = false
      }
    },
    openEdit(song) {
      this.selectedSong = song
      this.showEdit = true
    },
    downloadSong(song) {
      const src = this.songSource(song)
      if (!src) {
        this.error = 'This song has no downloadable audio URL.'
        return
      }

      const safeTitle = (song?.title || 'song')
        .trim()
        .replace(/[^a-z0-9-_]+/gi, '_')
        .replace(/^_+|_+$/g, '')

      const link = document.createElement('a')
      link.href = src
      link.download = `${safeTitle || 'song'}.mp3`
      link.target = '_blank'
      link.rel = 'noopener noreferrer'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    openShare(song) {
      this.selectedSong = song
      this.showShare = true
    },
    closeEdit() {
      this.showEdit = false
      this.selectedSong = null
    },
    closeShare() {
      this.showShare = false
      this.selectedSong = null
    },
    async deleteSong(song) {
      try {
        await deleteSongById(song.id)
        this.songs = this.songs.filter((s) => s.id !== song.id)
        if (this.currentSong && this.currentSong.id === song.id) {
          const audio = this.$refs.audioPlayer
          if (audio) {
            audio.pause()
            audio.currentTime = 0
          }
          this.currentSong = null
          this.isPlaying = false
          this.currentTime = 0
          this.duration = 0
        }
      } catch (err) {
        this.error = err?.response?.data?.error || 'Failed to delete song.'
      }
    },
    onSongSaved(updatedSong) {
      this.songs = this.songs.map((song) =>
        song.id === updatedSong.id ? { ...song, ...updatedSong } : song
      )
      this.closeEdit()
    },
    async onGenerated(generation) {
      this.showGenerate = false
      this.error = ''
      this.activeGenerationId = generation?.id || null
      if (this.activeGenerationId) {
        this.generationMessage = 'Generation submitted. Waiting for Suno to finish...'
        this.scheduleGenerationPoll()
      } else {
        await this.loadSongs()
      }
    },
  },
}
</script>

<style scoped>
.filter-select {
  appearance: none;
  -webkit-appearance: none;
  padding-right: 2.25rem;
}
</style>