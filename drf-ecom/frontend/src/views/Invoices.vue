<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Factures</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="fas fa-plus me-2"></i>Nouvelle facture
      </button>
    </div>

    <!-- Filtres par période -->
    <div class="row mb-3">
      <div class="col-md-3">
        <label class="form-label">Année</label>
        <select class="form-select" v-model="filters.year" @change="filterByPeriod">
          <option value="">Toutes les années</option>
          <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label">Trimestre</label>
        <select class="form-select" v-model="filters.quarter" @change="filterByPeriod">
          <option value="">Tous les trimestres</option>
          <option value="1">T1 (Jan-Mar)</option>
          <option value="2">T2 (Avr-Juin)</option>
          <option value="3">T3 (Juil-Sep)</option>
          <option value="4">T4 (Oct-Déc)</option>
        </select>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status"></div>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>N° Facture</th>
                <th>Client</th>
                <th>Date</th>
                <th>Échéance</th>
                <th>Montant HT</th>
                <th>TVA</th>
                <th>Montant TTC</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="invoice in invoices" :key="invoice.id">
                <td><strong>{{ invoice.invoice_number }}</strong></td>
                <td>{{ invoice.customer_name || invoice.supplier_name }}</td>
                <td>{{ formatDate(invoice.invoice_date) }}</td>
                <td>{{ formatDate(invoice.due_date) }}</td>
                <td>€{{ invoice.subtotal_excl_vat }}</td>
                <td>€{{ invoice.vat_amount }}</td>
                <td>€{{ invoice.total_incl_vat }}</td>
                <td>
                  <span :class="statusClass(invoice.status)">
                    {{ statusText(invoice.status) }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="viewInvoice(invoice)">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-success me-1" @click="downloadPDF(invoice)">
                    <i class="fas fa-download"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-info me-1" @click="sendEmail(invoice)" :disabled="!invoice.customer">
                    <i class="fas fa-envelope"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal création -->
    <div class="modal fade" :class="{ show: showCreateModal }" :style="{ display: showCreateModal ? 'block' : 'none' }">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Nouvelle facture</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveInvoice">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Type de facture</label>
                    <select class="form-select" v-model="invoiceForm.invoice_type" required>
                      <option value="sale">Facture de vente</option>
                      <option value="purchase">Facture d'achat</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Client *</label>
                    <select class="form-select" v-model="invoiceForm.customer" required>
                      <option value="">Sélectionner un client</option>
                      <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                        {{ customer.user.first_name }} {{ customer.user.last_name }} - {{ customer.user.email }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Date de facture</label>
                    <input type="date" class="form-control" v-model="invoiceForm.invoice_date" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Date d'échéance</label>
                    <input type="date" class="form-control" v-model="invoiceForm.due_date" required>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Date d'échéance</label>
                    <input type="date" class="form-control" v-model="invoiceForm.due_date" required>
                  </div>
                </div>
              </div>

              <h6>Lignes de facture</h6>
              <div class="table-responsive">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>Description</th>
                      <th>Quantité</th>
                      <th>Prix HT</th>
                      <th>TVA %</th>
                      <th>Total HT</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(line, index) in invoiceForm.lines" :key="index">
                      <td>
                        <input type="text" class="form-control form-control-sm" v-model="line.description" required>
                      </td>
                      <td>
                        <input type="number" class="form-control form-control-sm" v-model="line.quantity" @input="calculateLine(line)" required>
                      </td>
                      <td>
                        <input type="number" step="0.01" class="form-control form-control-sm" v-model="line.unit_price_excl_vat" @input="calculateLine(line)" required>
                      </td>
                      <td>
                        <select class="form-select form-select-sm" v-model="line.vat_rate" @change="calculateLine(line)">
                          <option value="21">21%</option>
                          <option value="6">6%</option>
                          <option value="0">0%</option>
                        </select>
                      </td>
                      <td>€{{ line.total_excl_vat || 0 }}</td>
                      <td>
                        <button type="button" class="btn btn-sm btn-outline-danger" @click="removeLine(index)">
                          <i class="fas fa-trash"></i>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <button type="button" class="btn btn-sm btn-outline-primary mb-3" @click="addLine">
                <i class="fas fa-plus me-2"></i>Ajouter une ligne
              </button>

              <div class="row">
                <div class="col-md-8"></div>
                <div class="col-md-4">
                  <table class="table table-sm">
                    <tr>
                      <td><strong>Total HT:</strong></td>
                      <td class="text-end"><strong>€{{ totalHT }}</strong></td>
                    </tr>
                    <tr>
                      <td><strong>TVA:</strong></td>
                      <td class="text-end"><strong>€{{ totalVAT }}</strong></td>
                    </tr>
                    <tr>
                      <td><strong>Total TTC:</strong></td>
                      <td class="text-end"><strong>€{{ totalTTC }}</strong></td>
                    </tr>
                  </table>
                </div>
              </div>
              
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">Annuler</button>
                <button type="submit" class="btn btn-primary">Créer la facture</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'Invoices',
  data() {
    return {
      showCreateModal: false,
      customers: [],
      filters: {
        year: '',
        quarter: ''
      },
      availableYears: [2024, 2023, 2022],
      invoiceForm: {
        invoice_type: 'sale',
        customer: '',
        invoice_date: new Date().toISOString().split('T')[0],
        due_date: this.getDefaultDueDate(),
        lines: [
          {
            description: '',
            quantity: 1,
            unit_price_excl_vat: 0,
            vat_rate: 21,
            total_excl_vat: 0
          }
        ]
      }
    }
  },
  computed: {
    ...mapState('invoices', ['invoices', 'loading']),
    totalHT() {
      return this.invoiceForm.lines.reduce((sum, line) => sum + (parseFloat(line.total_excl_vat) || 0), 0).toFixed(2)
    },
    totalVAT() {
      return this.invoiceForm.lines.reduce((sum, line) => {
        const ht = parseFloat(line.total_excl_vat) || 0
        const vatRate = parseFloat(line.vat_rate) || 0
        return sum + (ht * vatRate / 100)
      }, 0).toFixed(2)
    },
    totalTTC() {
      return (parseFloat(this.totalHT) + parseFloat(this.totalVAT)).toFixed(2)
    }
  },
  methods: {
    ...mapActions('invoices', ['fetchInvoices', 'createInvoice']),
    formatDate(date) {
      return new Date(date).toLocaleDateString('fr-FR')
    },
    statusClass(status) {
      const classes = {
        draft: 'badge bg-secondary',
        sent: 'badge bg-primary',
        paid: 'badge bg-success',
        overdue: 'badge bg-danger',
        cancelled: 'badge bg-dark'
      }
      return classes[status] || 'badge bg-secondary'
    },
    statusText(status) {
      const texts = {
        draft: 'Brouillon',
        sent: 'Envoyée',
        paid: 'Payée',
        overdue: 'En retard',
        cancelled: 'Annulée'
      }
      return texts[status] || status
    },
    calculateLine(line) {
      const quantity = parseFloat(line.quantity) || 0
      const unitPrice = parseFloat(line.unit_price_excl_vat) || 0
      line.total_excl_vat = (quantity * unitPrice).toFixed(2)
    },
    addLine() {
      this.invoiceForm.lines.push({
        description: '',
        quantity: 1,
        unit_price_excl_vat: 0,
        vat_rate: 21,
        total_excl_vat: 0
      })
    },
    removeLine(index) {
      this.invoiceForm.lines.splice(index, 1)
    },
    async saveInvoice() {
      try {
        await this.createInvoice(this.invoiceForm)
        this.closeModal()
        this.fetchInvoices()
      } catch (error) {
        console.error('Error creating invoice:', error)
      }
    },
    getDefaultDueDate() {
      const date = new Date()
      date.setDate(date.getDate() + 30)
      return date.toISOString().split('T')[0]
    },
    async fetchCustomers() {
      try {
        const response = await this.$store.dispatch('customers/fetchCustomers')
        this.customers = response || []
      } catch (error) {
        console.error('Error fetching customers:', error)
      }
    },
    async downloadPDF(invoice) {
      try {
        const response = await fetch(`/api/admin-dashboard/invoices/${invoice.id}/download_pdf/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        
        if (response.ok) {
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `facture_${invoice.invoice_number}.pdf`
          a.click()
          window.URL.revokeObjectURL(url)
        }
      } catch (error) {
        console.error('Error downloading PDF:', error)
      }
    },
    async sendEmail(invoice) {
      if (!invoice.customer) {
        alert('Aucun client associé à cette facture')
        return
      }
      
      try {
        const response = await fetch(`/api/admin-dashboard/invoices/${invoice.id}/send_email/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          }
        })
        
        const data = await response.json()
        if (response.ok) {
          alert('Email envoyé avec succès !')
        } else {
          alert(`Erreur: ${data.error}`)
        }
      } catch (error) {
        console.error('Error sending email:', error)
        alert('Erreur lors de l\'envoi de l\'email')
      }
    },
    async filterByPeriod() {
      try {
        const params = new URLSearchParams()
        if (this.filters.year) params.append('year', this.filters.year)
        if (this.filters.quarter) params.append('quarter', this.filters.quarter)
        
        const response = await fetch(`/api/admin-dashboard/invoices/by_period/?${params}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          this.$store.commit('invoices/SET_INVOICES', data)
        }
      } catch (error) {
        console.error('Error filtering invoices:', error)
      }
    },
    viewInvoice(invoice) {
      console.log('View invoice:', invoice)
    },
    closeModal() {
      this.showCreateModal = false
      this.invoiceForm = {
        invoice_type: 'sale',
        customer: '',
        invoice_date: new Date().toISOString().split('T')[0],
        due_date: this.getDefaultDueDate(),
        lines: [
          {
            description: '',
            quantity: 1,
            unit_price_excl_vat: 0,
            vat_rate: 21,
            total_excl_vat: 0
          }
        ]
      }
    }
  },
  mounted() {
    this.fetchInvoices()
    this.fetchCustomers()
  }
}
</script>

<style scoped>
.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>