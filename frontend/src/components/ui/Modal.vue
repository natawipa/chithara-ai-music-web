<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/45 p-4" @click.self="$emit('close')">
    <div class="w-full max-w-2xl rounded-2xl border border-white/60 bg-white/75 shadow-2xl backdrop-blur-2xl">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModalShell',
  emits: ['close'],
}
</script>