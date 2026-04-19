import api from './client'

export async function getLibrarySongs() {
	const response = await api.get('/songs/')
	return response.data
}

export async function updateSong(id, payload) {
	const response = await api.post(`/songs/${id}/update/`, payload)
	return response.data
}

export async function deleteSongById(id) {
	const response = await api.delete(`/songs/${id}/delete/`)
	return response.data
}

export async function uploadCoverImage(id, file) {
	const formData = new FormData()
	formData.append('cover_image', file)
	const response = await api.post(`/songs/${id}/upload-cover/`, formData, {
		headers: { 'Content-Type': 'multipart/form-data' },
	})
	return response.data
}

