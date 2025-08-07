import api from '../../services/api'

export default {
  namespaced: true,
  state: {
    entries: [],
    chartOfAccounts: [],
    vatDeclarations: [],
    loading: false
  },
  mutations: {
    SET_ENTRIES(state, entries) {
      state.entries = entries
    },
    SET_CHART_OF_ACCOUNTS(state, accounts) {
      state.chartOfAccounts = accounts
    },
    SET_VAT_DECLARATIONS(state, declarations) {
      state.vatDeclarations = declarations
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    }
  },
  actions: {
    async fetchEntries({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await api.getAccountingEntries()
        commit('SET_ENTRIES', response.data.results || response.data)
      } catch (error) {
        console.error('Error fetching entries:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async fetchChartOfAccounts({ commit }) {
      try {
        const response = await api.getChartOfAccounts()
        commit('SET_CHART_OF_ACCOUNTS', response.data.results || response.data)
      } catch (error) {
        console.error('Error fetching chart of accounts:', error)
      }
    },
    async fetchVATDeclarations({ commit }) {
      try {
        const response = await api.getVATDeclarations()
        commit('SET_VAT_DECLARATIONS', response.data.results || response.data)
      } catch (error) {
        console.error('Error fetching VAT declarations:', error)
      }
    }
  }
}