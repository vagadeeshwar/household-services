// frontend/src/store/index.js
import { createStore } from 'vuex'
import auth from './modules/auth'
import profile from './modules/profile'

export default createStore({
    modules: {
        auth,
        profile
    }
})