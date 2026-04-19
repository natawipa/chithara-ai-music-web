import axios from 'axios'

function getCsrfToken() {
	const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/)
	return match ? match[1] : ''
}

const api = axios.create({
	baseURL: '/api',
	withCredentials: true,
})

api.interceptors.request.use((config) => {
	const token = getCsrfToken()
	if (token) {
		config.headers['X-CSRFToken'] = token
	}
	return config
})

export default api
