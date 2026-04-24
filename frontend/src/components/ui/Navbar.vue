<template>
  <header :class="navbarClasses">
    <div class="mx-auto flex max-w-7xl items-center justify-between pl-2 pr-6 py-5">

      <!-- Left -->
      <div class="flex items-center gap-2">
        <img :src="logoHorizontal" alt="Chithara logo" class="h-13 w-auto" />
      </div>

      <!-- Right -->
      <div class="flex items-center gap-2">
        <button
          v-if="showGenerateButton"
          class="app-btn gap-2 px-4 py-2 text-sm text-[#141414] bg-white hover:bg-amber-400/35"
          @click="$emit('generate')"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="h-4 w-4"
            aria-hidden="true"
          >
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>
          Generate
        </button>

        <button
          v-if="showLogoutButton"
          class="app-btn gap-2 px-4 py-2 text-sm text-[#141414] bg-white hover:bg-amber-400/35 disabled:opacity-60"
          :disabled="isLoggingOut"
          @click="handleLogout"
        >
          <LogOut class="h-4 w-4" />
          {{ isLoggingOut ? 'Logging out...' : 'Logout' }}
        </button>

        <slot name="right" />
      </div>

    </div>
  </header>
</template>

<script>
import { LogOut } from 'lucide-vue-next'
import { logoutSession } from '../../api/auth'
import logoHorizontal from '../../assets/logo/logo-horizontal.svg'

export default {
  name: 'UiNavbar',
  components: {
    LogOut,
  },
  emits: ['generate'],
  props: {
    sticky: {
      type: Boolean,
      default: true,
    },
    showGenerateButton: {
      type: Boolean,
      default: false,
    },
    showLogoutButton: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isLoggingOut: false,
      logoHorizontal,
    }
  },
  computed: {
    navbarClasses() {
      return [
        'library-navbar',
        this.sticky ? 'sticky top-0 z-40' : '',
      ]
    },
  },
  methods: {
    async handleLogout() {
      if (this.isLoggingOut) return

      this.isLoggingOut = true
      try {
        await logoutSession()
      } catch (_) {
        // Continue to landing even if the session is already invalid.
      } finally {
        this.isLoggingOut = false
      }

      if (this.$router) {
        this.$router.push('/')
        return
      }

      window.location.href = '/'
    },
  },
}
</script>

<style scoped>
.library-navbar {
  background-color: rgba(0, 0, 0, 0.01); 
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}
</style>