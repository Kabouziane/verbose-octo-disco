import api from '../../services/api'

export default {
  namespaced: true,
  state: {
    user: null,
    token: localStorage.getItem('access_token'),
    isAuthenticated: !!localStorage.getItem('access_token')
  },
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKEN(state, token) {
      state.token = token
      state.isAuthenticated = !!token
    }
  },
  actions: {
    async login({ commit }, credentials) {
      try {
        const response = await api.login(credentials)
        const { access, refresh } = response.data
        
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)
        
        commit('SET_TOKEN', access)
        return response.data
      } catch (error) {
        throw error
      }
    },
    logout({ commit }) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
    }
  }
}