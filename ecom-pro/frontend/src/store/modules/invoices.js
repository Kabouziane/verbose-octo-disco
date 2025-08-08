import api from '../../services/api'

export default {
  namespaced: true,
  state: {
    invoices: [],
    loading: false
  },
  mutations: {
    SET_INVOICES(state, invoices) {
      state.invoices = invoices
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    ADD_INVOICE(state, invoice) {
      state.invoices.unshift(invoice)
    }
  },
  actions: {
    async fetchInvoices({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await api.getInvoices()
        commit('SET_INVOICES', response.data.results || response.data)
      } catch (error) {
        console.error('Error fetching invoices:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async createInvoice({ commit }, invoiceData) {
      try {
        const response = await api.createInvoice(invoiceData)
        commit('ADD_INVOICE', response.data)
        return response.data
      } catch (error) {
        throw error
      }
    }
  }
}