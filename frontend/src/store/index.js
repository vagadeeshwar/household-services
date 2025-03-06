import { createStore } from 'vuex'

import auth from './modules/auth'
import services from './modules/services'
import requests from './modules/requests'
import professionals from './modules/professionals'
import customers from './modules/customers'
import stats from './modules/stats'
import exports from './modules/exports'
import apiCache from './modules/apiCache'

export default createStore({
  modules: {
    auth,
    services,
    requests,
    professionals,
    customers,
    stats,
    exports,
    apiCache,
  },
  // Enable strict mode in development
  strict: true,
})
