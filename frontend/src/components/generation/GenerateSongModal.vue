<template>
	<Modal @close="$emit('close')">
		<div class="space-y-5 p-6">
			<div class="flex items-center justify-between border-b border-black/10 pb-4">
				<h3 class="text-2xl font-semibold text-neutral-900">Generate Song</h3>
				<button class="rounded-lg p-2 hover:bg-black/5" @click="$emit('close')">
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
					<label class="grid gap-2 text-sm font-medium">
						Genre
						<select v-model="form.genre" class="rounded-xl border border-black/15 bg-white/60 px-3 py-2">
							<option value="">Select genre</option>
							<option value="CLASSICAL">Classical</option>
							<option value="JAZZ">Jazz</option>
							<option value="ROCK">Rock</option>
							<option value="POP">Pop</option>
							<option value="ELECTRONIC">Electronic</option>
						</select>
					</label>

					<label class="grid gap-2 text-sm font-medium">
						Tone
						<select v-model="form.tone" class="rounded-xl border border-black/15 bg-white/60 px-3 py-2">
							<option value="">Select tone</option>
							<option value="CALM">Calm</option>
							<option value="ENERGETIC">Energetic</option>
							<option value="HAPPY">Happy</option>
							<option value="ROMANTIC">Romantic</option>
							<option value="SAD">Sad</option>
						</select>
					</label>
				</div>

				<label class="grid gap-2 text-sm font-medium">
					Occasion (optional)
					<select v-model="form.occasion" class="rounded-xl border border-black/15 bg-white/60 px-3 py-2">
						<option value="">None</option>
						<option value="BIRTHDAY">Birthday</option>
						<option value="PARTY">Party</option>
						<option value="RELAX">Relax</option>
						<option value="WORKOUT">Workout</option>
					</select>
				</label>

				<div v-if="error" class="rounded-xl border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
					{{ error }}
				</div>
			</div>

			<div class="flex items-center justify-end gap-3 border-t border-black/10 pt-4">
				<button class="rounded-xl border border-black/15 bg-white px-4 py-2 text-sm font-semibold" @click="$emit('close')">
					Cancel
				</button>
				<button
					class="inline-flex items-center gap-2 rounded-xl bg-amber-400 px-4 py-2 text-sm font-semibold text-neutral-900 hover:bg-amber-300 disabled:opacity-60"
					@click="submit"
					:disabled="submitting"
				>
					<WandSparkles class="h-4 w-4" />
					Generate
				</button>
			</div>
		</div>
	</Modal>
</template>

<script>
import Modal from '../ui/Modal.vue'
import { createGeneration } from '../../api/generation'
import { WandSparkles, X } from 'lucide-vue-next'

export default {
	name: 'GenerateSongModal',
	components: { Modal, WandSparkles, X },
	emits: ['close', 'generated'],
	data() {
		return {
			submitting: false,
			error: '',
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

			if (!this.form.title || !this.form.description || !this.form.genre || !this.form.tone) {
				this.error = 'Title, description, genre, and tone are required.'
				return
			}

			this.submitting = true
			try {
				const generation = await createGeneration({ ...this.form })
				this.$emit('generated', generation)
			} catch (err) {
				this.error = err?.response?.data?.error || 'Failed to create generation.'
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
</style>
