import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../pages/LandingPage.vue'
import LibraryPage from '../pages/LibraryPage.vue'

const router = createRouter({
	history: createWebHistory(),
	routes: [
		{ path: '/', name: 'landing', component: LandingPage },
		{ path: '/library', name: 'library', component: LibraryPage },
	],
})

export default router
