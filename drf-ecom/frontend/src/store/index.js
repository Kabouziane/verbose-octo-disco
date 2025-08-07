import { createStore } from 'vuex'
import auth from './modules/auth'
import products from './modules/products'
import invoices from './modules/invoices'
import accounting from './modules/accounting'

export default createStore({
  modules: {
    auth,
    products,
    invoices,
    accounting
  }
})