import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

// Configuration axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Intercepteur pour ajouter le token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Intercepteur pour gérer les erreurs d'authentification
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expiré, essayer de le rafraîchir
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken
          })
          localStorage.setItem('access_token', response.data.access)
          // Retry la requête originale
          error.config.headers.Authorization = `Bearer ${response.data.access}`
          return api.request(error.config)
        } catch (refreshError) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default {
  // Auth
  login: (credentials) => api.post('/auth/token/', credentials),
  refreshToken: (refresh) => api.post('/auth/token/refresh/', { refresh }),

  // Shop
  getProducts: () => api.get('/shop/products/'),
  getProduct: (id) => api.get(`/shop/products/${id}/`),
  getCategories: () => api.get('/shop/categories/'),
  getOrders: () => api.get('/shop/orders/'),
  createOrder: (data) => api.post('/shop/orders/', data),
  getCustomers: () => api.get('/shop/customers/'),

  // Admin Dashboard
  getInvoices: () => api.get('/admin-dashboard/invoices/'),
  createInvoice: (data) => api.post('/admin-dashboard/invoices/', data),
  getAccountingEntries: () => api.get('/admin-dashboard/entries/'),
  createAccountingEntry: (data) => api.post('/admin-dashboard/entries/', data),
  getChartOfAccounts: () => api.get('/admin-dashboard/chart-of-accounts/'),
  getVATDeclarations: () => api.get('/admin-dashboard/vat-declarations/'),
  generateVATDeclaration: (data) => api.post('/admin-dashboard/vat-declarations/generate_declaration/', data),
  getEmployees: () => api.get('/admin-dashboard/employees/'),

  // Services
  getServices: () => api.get('/service/services/'),
  getAppointments: () => api.get('/service/appointments/'),
  createAppointment: (data) => api.post('/service/appointments/', data),
  getSupportTickets: () => api.get('/service/tickets/'),
  createSupportTicket: (data) => api.post('/service/tickets/', data),
}