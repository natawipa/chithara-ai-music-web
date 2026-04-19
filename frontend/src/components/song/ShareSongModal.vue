<template>
	<Modal @close="$emit('close')">
		<div class="space-y-5 p-6">
			<div class="flex items-center justify-between border-b border-black/10 pb-4">
				<h3 class="text-xl font-semibold">Share Song</h3>
				<button class="rounded-lg p-2 hover:bg-black/5" @click="$emit('close')">
					<X class="h-5 w-5" />
				</button>
			</div>

			<div class="rounded-xl border border-black/15 bg-white/60 p-3 text-sm break-all">
				{{ shareLink }}
			</div>

			<div class="flex items-center justify-end gap-3 border-t border-black/10 pt-4">
				<button class="rounded-xl border border-black/15 bg-white px-4 py-2 text-sm font-semibold" @click="$emit('close')">
					Close
				</button>
				<button
					class="inline-flex items-center gap-2 rounded-xl bg-neutral-900 px-4 py-2 text-sm font-semibold text-white hover:bg-neutral-800"
					@click="copyLink"
				>
					<Copy class="h-4 w-4" />
					Copy
				</button>
			</div>

			<p v-if="copied" class="text-sm text-emerald-700">Link copied.</p>
		</div>
	</Modal>
</template>

<script>
import Modal from '../ui/Modal.vue'
import { Copy, X } from 'lucide-vue-next'

export default {
	name: 'ShareSongModal',
	components: { Modal, Copy, X },
	props: {
		song: {
			type: Object,
			required: true,
		},
	},
	emits: ['close'],
	data() {
		return {
			copied: false,
		}
	},
	computed: {
		shareLink() {
			return this.song?.share_url || `${window.location.origin}/song/${this.song?.id}`
		},
	},
	methods: {
		async copyLink() {
			this.copied = false
			try {
				await navigator.clipboard.writeText(this.shareLink)
				this.copied = true
			} catch (_) {
				this.copied = false
			}
		},
	},
}
</script>

<style scoped>
</style>
