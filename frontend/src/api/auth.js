import api from './client'

export async function logoutSession() {
	const response = await api.post('/auth/logout/')
	return response.data
}