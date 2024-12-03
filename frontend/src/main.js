import * as bootstrap from 'bootstrap' // eslint-disable-line

import { createApp } from 'vue'

import './assets/styles.scss'
import 'bootstrap-icons/font/bootstrap-icons.css'

import App from './App.vue'
import router from './router'
import store from './store'

import Loading from '@/components/shared/Loading.vue'
import Toast from '@/components/shared/Toast.vue'
import FormNavigationGuard from '@/components/shared/FormNavigationGuard.vue'

const app = createApp(App)

// Register global components
app.component('Loading', Loading)
app.component('Toast', Toast)
app.component('FormNavigationGuard', FormNavigationGuard)

app.use(router)
app.use(store)

app.mount('#app')
