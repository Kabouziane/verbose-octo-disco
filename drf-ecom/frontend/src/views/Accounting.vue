<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Comptabilité</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="fas fa-plus me-2"></i>Nouvelle écriture
      </button>
    </div>

    <!-- Onglets -->
    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'entries' }" @click="activeTab = 'entries'">
          Écritures comptables
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'accounts' }" @click="activeTab = 'accounts'">
          Plan comptable
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'balance' }" @click="activeTab = 'balance'">
          Balance
        </a>
      </li>
    </ul>

    <!-- Écritures comptables -->
    <div v-if="activeTab === 'entries'" class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status"></div>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>N° Écriture</th>
                <th>Date</th>
                <th>Journal</th>
                <th>Description</th>
                <th>Débit</th>
                <th>Crédit</th>
                <th>Équilibrée</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in entries" :key="entry.id">
                <td><strong>{{ entry.entry_number }}</strong></td>
                <td>{{ formatDate(entry.entry_date) }}</td>
                <td>{{ entry.journal_name }}</td>
                <td>{{ entry.description }}</td>
                <td>€{{ entry.total_debit }}</td>
                <td>€{{ entry.total_credit }}</td>
                <td>
                  <span :class="entry.is_balanced ? 'badge bg-success' : 'badge bg-danger'">
                    {{ entry.is_balanced ? 'Oui' : 'Non' }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Plan comptable -->
    <div v-if="activeTab === 'accounts'" class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>N° Compte</th>
                <th>Nom du compte</th>
                <th>Type</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="account in chartOfAccounts" :key="account.id">
                <td><strong>{{ account.account_number }}</strong></td>
                <td>{{ account.account_name }}</td>
                <td>
                  <span class="badge bg-info">
                    Classe {{ account.account_type }}
                  </span>
                </td>
                <td>
                  <span :class="account.is_active ? 'badge bg-success' : 'badge bg-secondary'">
                    {{ account.is_active ? 'Actif' : 'Inactif' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Balance -->
    <div v-if="activeTab === 'balance'" class="card">
      <div class="card-body">
        <div class="row mb-3">
          <div class="col-md-3">
            <label class="form-label">Date de début</label>
            <input type="date" class="form-control" v-model="balanceFilters.dateFrom">
          </div>
          <div class="col-md-3">
            <label class="form-label">Date de fin</label>
            <input type="date" class="form-control" v-model="balanceFilters.dateTo">
          </div>
          <div class="col-md-3">
            <button class="btn btn-primary mt-4" @click="loadBalance">
              Générer la balance
            </button>
          </div>
        </div>
        
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>N° Compte</th>
                <th>Nom du compte</th>
                <th>Débit</th>
                <th>Crédit</th>
                <th>Solde</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(balance, accountNumber) in trialBalance" :key="accountNumber">
                <td><strong>{{ accountNumber }}</strong></td>
                <td>{{ balance.account_name }}</td>
                <td>€{{ balance.debit }}</td>
                <td>€{{ balance.credit }}</td>
                <td>
                  <span :class="(balance.debit - balance.credit) >= 0 ? 'text-success' : 'text-danger'">
                    €{{ Math.abs(balance.debit - balance.credit).toFixed(2) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal création écriture -->
    <div class="modal fade" :class="{ show: showCreateModal }" :style="{ display: showCreateModal ? 'block' : 'none' }">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Nouvelle écriture comptable</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveEntry">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Date</label>
                    <input type="date" class="form-control" v-model="entryForm.entry_date" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-control" v-model="entryForm.description" required>
                  </div>
                </div>
              </div>

              <h6>Lignes d'écriture</h6>
              <div class="table-responsive">
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>Compte</th>
                      <th>Description</th>
                      <th>Débit</th>
                      <th>Crédit</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(line, index) in entryForm.lines" :key="index">
                      <td>
                        <select class="form-select form-select-sm" v-model="line.account" required>
                          <option value="">Sélectionner un compte</option>
                          <option v-for="account in chartOfAccounts" :key="account.id" :value="account.id">
                            {{ account.account_number }} - {{ account.account_name }}
                          </option>
                        </select>
                      </td>
                      <td>
                        <input type="text" class="form-control form-control-sm" v-model="line.description" required>
                      </td>
                      <td>
                        <input type="number" step="0.01" class="form-control form-control-sm" v-model="line.debit_amount">
                      </td>
                      <td>
                        <input type="number" step="0.01" class="form-control form-control-sm" v-model="line.credit_amount">
                      </td>
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
                      <td><strong>Total Débit:</strong></td>
                      <td class="text-end"><strong>€{{ totalDebit }}</strong></td>
                    </tr>
                    <tr>
                      <td><strong>Total Crédit:</strong></td>
                      <td class="text-end"><strong>€{{ totalCredit }}</strong></td>
                    </tr>
                    <tr :class="isBalanced ? 'text-success' : 'text-danger'">
                      <td><strong>Équilibre:</strong></td>
                      <td class="text-end"><strong>{{ isBalanced ? 'OK' : 'KO' }}</strong></td>
                    </tr>
                  </table>
                </div>
              </div>
              
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">Annuler</button>
                <button type="submit" class="btn btn-primary" :disabled="!isBalanced">Enregistrer</button>
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
  name: 'Accounting',
  data() {
    return {
      activeTab: 'entries',
      showCreateModal: false,
      balanceFilters: {
        dateFrom: '',
        dateTo: ''
      },
      trialBalance: {},
      entryForm: {
        entry_date: new Date().toISOString().split('T')[0],
        description: '',
        lines: [
          {
            account: '',
            description: '',
            debit_amount: 0,
            credit_amount: 0
          },
          {
            account: '',
            description: '',
            debit_amount: 0,
            credit_amount: 0
          }
        ]
      }
    }
  },
  computed: {
    ...mapState('accounting', ['entries', 'chartOfAccounts', 'loading']),
    totalDebit() {
      return this.entryForm.lines.reduce((sum, line) => sum + (parseFloat(line.debit_amount) || 0), 0).toFixed(2)
    },
    totalCredit() {
      return this.entryForm.lines.reduce((sum, line) => sum + (parseFloat(line.credit_amount) || 0), 0).toFixed(2)
    },
    isBalanced() {
      return parseFloat(this.totalDebit) === parseFloat(this.totalCredit)
    }
  },
  methods: {
    ...mapActions('accounting', ['fetchEntries', 'fetchChartOfAccounts']),
    formatDate(date) {
      return new Date(date).toLocaleDateString('fr-FR')
    },
    addLine() {
      this.entryForm.lines.push({
        account: '',
        description: '',
        debit_amount: 0,
        credit_amount: 0
      })
    },
    removeLine(index) {
      if (this.entryForm.lines.length > 2) {
        this.entryForm.lines.splice(index, 1)
      }
    },
    async loadBalance() {
      // API call to get trial balance
      console.log('Load balance for period:', this.balanceFilters)
    },
    async saveEntry() {
      try {
        // API call to create entry
        console.log('Save entry:', this.entryForm)
        this.closeModal()
        this.fetchEntries()
      } catch (error) {
        console.error('Error creating entry:', error)
      }
    },
    closeModal() {
      this.showCreateModal = false
      this.entryForm = {
        entry_date: new Date().toISOString().split('T')[0],
        description: '',
        lines: [
          {
            account: '',
            description: '',
            debit_amount: 0,
            credit_amount: 0
          },
          {
            account: '',
            description: '',
            debit_amount: 0,
            credit_amount: 0
          }
        ]
      }
    }
  },
  mounted() {
    this.fetchEntries()
    this.fetchChartOfAccounts()
  }
}
</script>

<style scoped>
.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.nav-link {
  cursor: pointer;
}
</style>