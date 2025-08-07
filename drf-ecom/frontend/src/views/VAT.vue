<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Déclarations TVA</h1>
      <button class="btn btn-primary" @click="showGenerateModal = true">
        <i class="fas fa-plus me-2"></i>Générer déclaration
      </button>
    </div>

    <!-- Statistiques TVA -->
    <div class="row mb-4">
      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                  TVA à payer ce mois
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">€8,400</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-percentage fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-success shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                  TVA déductible
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">€2,100</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-arrow-down fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-info shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                  Opérations 21%
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">€40,000</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-chart-bar fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-warning shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                  Opérations 6%
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">€10,000</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-chart-pie fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Liste des déclarations -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status"></div>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Période</th>
                <th>Type</th>
                <th>Opérations 21%</th>
                <th>Opérations 6%</th>
                <th>TVA due</th>
                <th>TVA déductible</th>
                <th>Solde</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="declaration in vatDeclarations" :key="declaration.id">
                <td>
                  <strong>{{ formatPeriod(declaration) }}</strong>
                </td>
                <td>
                  <span class="badge bg-info">
                    {{ declaration.period_type === 'monthly' ? 'Mensuelle' : 'Trimestrielle' }}
                  </span>
                </td>
                <td>€{{ declaration.grid_03_operations_21_percent }}</td>
                <td>€{{ declaration.grid_01_operations_6_percent }}</td>
                <td>€{{ (parseFloat(declaration.grid_56_vat_21_percent) + parseFloat(declaration.grid_54_vat_6_percent)).toFixed(2) }}</td>
                <td>€{{ declaration.grid_59_vat_deductible }}</td>
                <td>
                  <span :class="parseFloat(declaration.grid_71_vat_to_pay) > 0 ? 'text-danger' : 'text-success'">
                    €{{ Math.abs(parseFloat(declaration.grid_71_vat_to_pay) - parseFloat(declaration.grid_72_vat_to_recover)).toFixed(2) }}
                  </span>
                </td>
                <td>
                  <span :class="declaration.is_submitted ? 'badge bg-success' : 'badge bg-warning'">
                    {{ declaration.is_submitted ? 'Soumise' : 'Brouillon' }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="viewDeclaration(declaration)">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-success me-1" v-if="!declaration.is_submitted">
                    <i class="fas fa-paper-plane"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-info">
                    <i class="fas fa-download"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal génération déclaration -->
    <div class="modal fade" :class="{ show: showGenerateModal }" :style="{ display: showGenerateModal ? 'block' : 'none' }">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Générer une déclaration TVA</h5>
            <button type="button" class="btn-close" @click="closeGenerateModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="generateDeclaration">
              <div class="mb-3">
                <label class="form-label">Type de déclaration</label>
                <select class="form-select" v-model="declarationForm.period_type" required>
                  <option value="monthly">Mensuelle</option>
                  <option value="quarterly">Trimestrielle</option>
                </select>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Année</label>
                <input type="number" class="form-control" v-model="declarationForm.year" :min="2020" :max="2030" required>
              </div>
              
              <div class="mb-3">
                <label class="form-label">
                  {{ declarationForm.period_type === 'monthly' ? 'Mois' : 'Trimestre' }}
                </label>
                <select class="form-select" v-model="declarationForm.period" required>
                  <option v-if="declarationForm.period_type === 'monthly'" v-for="month in 12" :key="month" :value="month">
                    {{ getMonthName(month) }}
                  </option>
                  <option v-if="declarationForm.period_type === 'quarterly'" v-for="quarter in 4" :key="quarter" :value="quarter">
                    Trimestre {{ quarter }}
                  </option>
                </select>
              </div>
              
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeGenerateModal">Annuler</button>
                <button type="submit" class="btn btn-primary">Générer</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal détail déclaration -->
    <div class="modal fade" :class="{ show: showDetailModal }" :style="{ display: showDetailModal ? 'block' : 'none' }">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Déclaration TVA - {{ selectedDeclaration ? formatPeriod(selectedDeclaration) : '' }}</h5>
            <button type="button" class="btn-close" @click="closeDetailModal"></button>
          </div>
          <div class="modal-body" v-if="selectedDeclaration">
            <div class="row">
              <div class="col-md-6">
                <h6>Opérations imposables</h6>
                <table class="table table-sm">
                  <tbody>
                    <tr>
                      <td>Grille 00 - Opérations exemptées:</td>
                      <td class="text-end">€{{ selectedDeclaration.grid_00_operations_exempted }}</td>
                    </tr>
                    <tr>
                      <td>Grille 01 - Opérations 6%:</td>
                      <td class="text-end">€{{ selectedDeclaration.grid_01_operations_6_percent }}</td>
                    </tr>
                    <tr>
                      <td>Grille 03 - Opérations 21%:</td>
                      <td class="text-end">€{{ selectedDeclaration.grid_03_operations_21_percent }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="col-md-6">
                <h6>TVA due</h6>
                <table class="table table-sm">
                  <tbody>
                    <tr>
                      <td>Grille 54 - TVA 6%:</td>
                      <td class="text-end">€{{ selectedDeclaration.grid_54_vat_6_percent }}</td>
                    </tr>
                    <tr>
                      <td>Grille 56 - TVA 21%:</td>
                      <td class="text-end">€{{ selectedDeclaration.grid_56_vat_21_percent }}</td>
                    </tr>
                    <tr>
                      <td>Grille 59 - TVA déductible:</td>
                      <td class="text-end">€{{ selectedDeclaration.grid_59_vat_deductible }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <hr>
            
            <div class="row">
              <div class="col-md-12">
                <h6>Solde</h6>
                <table class="table table-sm">
                  <tbody>
                    <tr>
                      <td><strong>Grille 71 - TVA à payer:</strong></td>
                      <td class="text-end"><strong>€{{ selectedDeclaration.grid_71_vat_to_pay }}</strong></td>
                    </tr>
                    <tr>
                      <td><strong>Grille 72 - TVA à récupérer:</strong></td>
                      <td class="text-end"><strong>€{{ selectedDeclaration.grid_72_vat_to_recover }}</strong></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeDetailModal">Fermer</button>
            <button type="button" class="btn btn-primary" v-if="selectedDeclaration && !selectedDeclaration.is_submitted">
              Soumettre la déclaration
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'VAT',
  data() {
    return {
      showGenerateModal: false,
      showDetailModal: false,
      selectedDeclaration: null,
      declarationForm: {
        period_type: 'monthly',
        year: new Date().getFullYear(),
        period: new Date().getMonth() + 1
      }
    }
  },
  computed: {
    ...mapState('accounting', ['vatDeclarations', 'loading'])
  },
  methods: {
    ...mapActions('accounting', ['fetchVATDeclarations']),
    formatPeriod(declaration) {
      if (declaration.period_type === 'monthly') {
        return `${this.getMonthName(declaration.period)} ${declaration.year}`
      } else {
        return `T${declaration.period} ${declaration.year}`
      }
    },
    getMonthName(month) {
      const months = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
      ]
      return months[month - 1]
    },
    viewDeclaration(declaration) {
      this.selectedDeclaration = declaration
      this.showDetailModal = true
    },
    async generateDeclaration() {
      try {
        console.log('Generate declaration:', this.declarationForm)
        this.closeGenerateModal()
        this.fetchVATDeclarations()
      } catch (error) {
        console.error('Error generating declaration:', error)
      }
    },
    closeGenerateModal() {
      this.showGenerateModal = false
    },
    closeDetailModal() {
      this.showDetailModal = false
      this.selectedDeclaration = null
    }
  },
  mounted() {
    this.fetchVATDeclarations()
  }
}
</script>

<style scoped>
.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.border-left-primary {
  border-left: 0.25rem solid #4e73df !important;
}
.border-left-success {
  border-left: 0.25rem solid #1cc88a !important;
}
.border-left-info {
  border-left: 0.25rem solid #36b9cc !important;
}
.border-left-warning {
  border-left: 0.25rem solid #f6c23e !important;
}
</style>