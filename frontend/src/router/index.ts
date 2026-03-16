import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/App.vue'),
    },
    {
      path: '/preview',
      name: 'preview',
      component: () => import('@/views/ReportPreview.vue'),
    },
  ],
})

export default router
