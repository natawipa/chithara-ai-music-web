import api from './client'

export async function createGeneration(payload) {
	const response = await api.post('/generate/', payload)
	return response.data
}

export async function getGenerationStatus(id) {
	const response = await api.get(`/generate/${id}/status/`)
	return response.data
}

