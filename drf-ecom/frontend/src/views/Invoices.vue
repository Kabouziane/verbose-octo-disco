<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Factures</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="fas fa-plus me-2"></i>Nouvelle facture
      </button>
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
                  <button class="btn btn-sm btn-outline-primary me-1">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-success me-1">
                    <i class="fas fa-download"></i>
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
                    <label class="form-label">Date de facture</label>
                    <input type="date" class="form-control" v-model="invoiceForm.invoice_date" required>
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
      invoiceForm: {
        invoice_type: 'sale',
        invoice_date: new Date().toISOString().split('T')[0],
        due_date: '',
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
    closeModal() {
      this.showCreateModal = false
      this.invoiceForm = {
        invoice_type: 'sale',
        invoice_date: new Date().toISOString().split('T')[0],
        due_date: '',
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
  }
}
</script>

<style scoped>
.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>