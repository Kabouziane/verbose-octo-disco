import api from '../../services/api'

export default {
  namespaced: true,
  state: {
    products: [],
    categories: [],
    loading: false
  },
  mutations: {
    SET_PRODUCTS(state, products) {
      state.products = products
    },
    SET_CATEGORIES(state, categories) {
      state.categories = categories
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    }
  },
  actions: {
    async fetchProducts({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await api.getProducts()
        commit('SET_PRODUCTS', response.data.results || response.data)
      } catch (error) {
        console.error('Error fetching products:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async fetchCategories({ commit }) {
      try {
        const response = await api.getCategories()
        commit('SET_CATEGORIES', response.data.results || response.data)
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }
  }
}