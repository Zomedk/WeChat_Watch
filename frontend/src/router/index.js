import { createRouter, createWebHistory } from 'vue-router'
import Articles from '../views/Articles.vue'
import Subscriptions from '../views/Subscriptions.vue'
import Settings from '../views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Articles',
    component: Articles
  },
  {
    path: '/subscriptions',
    name: 'Subscriptions',
    component: Subscriptions
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router