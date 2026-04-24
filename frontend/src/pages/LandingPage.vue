<template>
  <main class="relative">
    <!-- Background decoration -->
    <img
      :src="diskNotesSvg"
      alt=""
      class="pointer-events-none absolute left-0 top-1/2 -translate-y-1/2 select-none hidden md:block
             w-auto h-auto max-h-[75dvh]"
    />

    <!-- Main content -->
    <div
      class="landing-container relative z-10 flex flex-col items-center justify-center
             min-h-[100dvh] lg:translate-x-2"
    >
      <!-- Logo -->
      <img
        :src="logoVerticalSvg"
        alt="Chithara"
        class="landing-logo h-auto"
      />

      <!-- Playback -->
      <img
        :src="playbackControlsSvg"
        alt="Playback controls"
        class="landing-playback h-auto"
      />

      <!-- Button -->
      <button
        class="app-btn landing-button text-[#141414] bg-white
               hover:bg-amber-400/35"
        @click="handleLogin"
      >
        <img
          src="https://www.svgrepo.com/show/475656/google-color.svg"
          alt="Google"
          class="landing-icon"
        />
        <span>Continue with Google</span>
      </button>
    </div>
  </main>
</template>

<script>
import diskNotesSvg from '../assets/disk-notes.svg'
import logoVerticalSvg from '../assets/logo/logo-vertical.svg'
import playbackControlsSvg from '../assets/playback-controls.svg'

export default {
  name: 'LandingPage',
  data() {
    return {
      diskNotesSvg,
      logoVerticalSvg,
      playbackControlsSvg,
    }
  },
  methods: {
    handleLogin() {
      window.location.href = 'http://localhost:8000/api/auth/login/'
    },
  },
}
</script>

<style scoped>
.landing-container {
  transform: translateY(-3dvh) scale(1.1);
}

/* Responsive scaling */
@media (min-width: 768px) {
  .landing-container {
    transform: translateY(-3dvh) scale(1.25);
  }
}

@media (min-width: 1024px) {
  .landing-container {
    transform: translateY(-3dvh) scale(1.5);
  }
}

/* Sizes (keep your ratio) */
.landing-playback {
  width: 28dvh;
}

.landing-logo {
  width: 18.5dvh;
}

.landing-button {
  margin-top: 5dvh;
  width: 40dvh;
  padding: 1.5dvh 2dvh;
  font-size: 2dvh;
  gap: 1dvh;
}

.landing-icon {
  width: 2dvh;
  height: 2dvh;
}
</style>


