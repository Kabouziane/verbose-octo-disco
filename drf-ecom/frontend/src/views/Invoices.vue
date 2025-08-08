<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Factures</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="fas fa-plus me-2"></i>Nouvelle facture
      </button>
    </div>

    <!-- Message de succès -->
    <div v-if="showSuccessMessage" class="alert alert-success alert-dismissible fade show success-message" role="alert">
      <i class="fas fa-check-circle me-2"></i>{{ successMessage }}
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
                      <option value="credit_note">Note de crédit</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Client *</label>
                    <select class="form-select" v-model="invoiceForm.customer" required>
                      <option value="">Sélectionner un client</option>
                      <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                        {{ customer.is_business ? customer.company_name : (customer.user?.first_name + ' ' + customer.user?.last_name).trim() }} - {{ customer.user_email }}
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
                    <tbody>
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
                    </tbody>
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
// Imports Vuex supprimés - utilisation directe de l'API

export default {
  name: 'Invoices',
  data() {
    return {
      showCreateModal: false,
      showSuccessMessage: false,
      successMessage: '',
      customers: [],
      invoicesList: [],
      loading: false,
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
    invoices() {
      return this.invoicesList
    },
    totalHT() {
      const total = this.invoiceForm.lines.reduce((sum, line) => {
        const lineTotal = parseFloat(line.total_excl_vat) || 0
        return sum + lineTotal
      }, 0)
      return Math.round(total * 100) / 100
    },
    totalVAT() {
      const total = this.invoiceForm.lines.reduce((sum, line) => {
        const ht = parseFloat(line.total_excl_vat) || 0
        const vatRate = parseFloat(line.vat_rate) || 0
        const vatAmount = ht * vatRate / 100
        return sum + vatAmount
      }, 0)
      return Math.round(total * 100) / 100
    },
    totalTTC() {
      return Math.round((this.totalHT + this.totalVAT) * 100) / 100
    }
  },
  methods: {
    async fetchInvoices() {
      try {
        const response = await fetch('http://localhost:8000/api/admin-dashboard/invoices/')
        if (response.ok) {
          const data = await response.json()
          this.invoicesList = data.results || data
          console.log('Factures chargées:', this.invoicesList)
        }
      } catch (error) {
        console.error('Error fetching invoices:', error)
      }
    },
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
      const total = quantity * unitPrice
      line.total_excl_vat = Math.round(total * 100) / 100
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
      this.loading = true
      const payload = {
        invoice_type: this.invoiceForm.invoice_type,
        customer: parseInt(this.invoiceForm.customer),
        invoice_date: this.invoiceForm.invoice_date,
        due_date: this.invoiceForm.due_date,
        billing_address: 'Adresse par défaut',
        subtotal_excl_vat: this.totalHT,
        vat_amount: this.totalVAT,
        total_incl_vat: this.totalTTC,
        lines: this.invoiceForm.lines.map(line => {
          const totalExclVat = Number(line.total_excl_vat) || 0
          const vatRate = Number(line.vat_rate) || 0
          const vatAmount = totalExclVat * vatRate / 100
          const totalInclVat = totalExclVat + vatAmount
          
          return {
            description: String(line.description || ''),
            quantity: Number(line.quantity) || 1,
            unit_price_excl_vat: Number(line.unit_price_excl_vat) || 0,
            vat_rate: vatRate,
            total_excl_vat: Math.round(totalExclVat * 100) / 100,
            vat_amount: Math.round(vatAmount * 100) / 100,
            total_incl_vat: Math.round(totalInclVat * 100) / 100
          }
        })
      }
      
      console.log('Payload envoyé:', JSON.stringify(payload, null, 2))
      
      try {
        const response = await fetch('http://localhost:8000/api/admin-dashboard/invoices/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })
        
        if (response.ok) {
          this.successMessage = 'Facture créée avec succès !'
          this.showSuccessMessage = true
          setTimeout(() => {
            this.showSuccessMessage = false
          }, 2000)
          this.closeModal()
          this.fetchInvoices()
        } else {
          const errorData = await response.json()
          let errorMessage = 'Erreur lors de la création:\n'
          for (const [field, messages] of Object.entries(errorData)) {
            if (Array.isArray(messages)) {
              errorMessage += `${field}: ${messages.join(', ')}\n`
            } else {
              errorMessage += `${field}: ${messages}\n`
            }
          }
          alert(errorMessage)
        }
      } catch (error) {
        console.error('Error creating invoice:', error)
        alert('Erreur lors de la création de la facture')
      } finally {
        this.loading = false
      }
    },
    getDefaultDueDate() {
      const date = new Date()
      date.setDate(date.getDate() + 30)
      return date.toISOString().split('T')[0]
    },
    async fetchCustomers() {
      try {
        const response = await fetch('http://localhost:8000/api/shop/customers/')
        if (response.ok) {
          const data = await response.json()
          this.customers = data.results || data
          console.log('Clients chargés pour factures:', this.customers)
        }
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

.success-message {
  animation: fadeInOut 2s ease-in-out;
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translateY(-10px); }
  20% { opacity: 1; transform: translateY(0); }
  80% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-10px); }
}
</style>