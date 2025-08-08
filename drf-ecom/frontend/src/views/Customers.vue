<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Clients</h1>
      <button class="btn btn-primary" @click.prevent="openModal">
        <i class="fas fa-plus me-2"></i>Nouveau client
      </button>
    </div>

    <!-- Message de succès -->
    <div v-if="showSuccessMessage" class="alert alert-success alert-dismissible fade show success-message" role="alert">
      <i class="fas fa-check-circle me-2"></i>{{ successMessage }}
    </div>

    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Email</th>
                <th>Téléphone</th>
                <th>Type</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="customer in customers" :key="customer.id">
                <td><strong>{{ customer.is_business ? customer.company_name : (customer.user?.first_name + ' ' + customer.user?.last_name).trim() }}</strong></td>
                <td>{{ customer.user_email }}</td>
                <td>{{ customer.phone || '-' }}</td>
                <td>
                  <span v-if="customer.is_business" class="badge bg-success">Entreprise</span>
                  <span v-else class="badge bg-info">Particulier</span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="viewCustomer(customer)" title="Voir détails">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-secondary" @click="editCustomer(customer)" title="Modifier">
                    <i class="fas fa-edit"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="!customers || customers.length === 0">
                <td colspan="5" class="text-center text-muted">Aucun client trouvé</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal création client -->
    <div class="modal fade" :class="{ show: showCreateModal, 'd-block': showCreateModal }" :style="{ display: showCreateModal ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Nouveau client</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveCustomer">
              <!-- Validation TVA -->
              <div class="mb-4">
                <h6>Vérification TVA (optionnel)</h6>
                <div class="row">
                  <div class="col-md-8">
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="vatNumber" 
                      placeholder="Ex: BE0123456789"
                      @input="clearVatValidation"
                    >
                  </div>
                  <div class="col-md-4">
                    <button 
                      type="button" 
                      class="btn btn-outline-primary" 
                      @click="validateVAT"
                      :disabled="!vatNumber || vatValidating"
                    >
                      <span v-if="vatValidating" class="spinner-border spinner-border-sm me-2"></span>
                      Vérifier
                    </button>
                  </div>
                </div>
                <div v-if="vatResult" class="mt-2">
                  <div v-if="vatResult.valid" class="alert alert-success">
                    <i class="fas fa-check me-2"></i>TVA valide - Informations récupérées
                  </div>
                  <div v-else class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>{{ vatResult.error }} - Remplissez manuellement
                  </div>
                </div>
              </div>

              <!-- Informations utilisateur -->
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Prénom {{ !customerForm.is_business ? '*' : '' }}</label>
                    <input type="text" class="form-control" v-model="customerForm.first_name" :required="!customerForm.is_business">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Nom {{ !customerForm.is_business ? '*' : '' }}</label>
                    <input type="text" class="form-control" v-model="customerForm.last_name" :required="!customerForm.is_business">
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Email *</label>
                <input type="email" class="form-control" v-model="customerForm.email" required>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Téléphone</label>
                    <input type="tel" class="form-control" v-model="customerForm.phone">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Type de client</label>
                    <select class="form-select" v-model="customerForm.is_business">
                      <option :value="false">Particulier</option>
                      <option :value="true">Entreprise</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Informations entreprise -->
              <div v-if="customerForm.is_business">
                <div class="mb-3">
                  <label class="form-label">Nom de l'entreprise *</label>
                  <input type="text" class="form-control" v-model="customerForm.company_name" :required="customerForm.is_business">
                </div>
                <div class="mb-3">
                  <label class="form-label">Adresse de l'entreprise</label>
                  <textarea class="form-control" rows="3" v-model="customerForm.company_address"></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label">Numéro de TVA</label>
                  <input type="text" class="form-control" v-model="customerForm.vat_number">
                </div>
              </div>

              <!-- Informations bancaires -->
              <div class="mb-3">
                <label class="form-label">IBAN (optionnel)</label>
                <input type="text" class="form-control" v-model="customerForm.iban" placeholder="BE68 5390 0754 7034">
              </div>

              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">Annuler</button>
                <button type="submit" class="btn btn-primary">Créer le client</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal visualisation client -->
    <div class="modal fade" :class="{ show: showViewModal, 'd-block': showViewModal }" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Détails du client</h5>
            <button type="button" class="btn-close" @click="closeAllModals"></button>
          </div>
          <div class="modal-body" v-if="selectedCustomer">
            <div class="row">
              <div class="col-md-6">
                <div class="card">
                  <div class="card-header"><h6>Informations personnelles</h6></div>
                  <div class="card-body">
                    <p><strong>Nom:</strong> {{ selectedCustomer.full_name || selectedCustomer.company_name }}</p>
                    <p><strong>Email:</strong> {{ selectedCustomer.user_email }}</p>
                    <p><strong>Téléphone:</strong> {{ selectedCustomer.phone || 'Non renseigné' }}</p>
                    <p><strong>Type:</strong> 
                      <span v-if="selectedCustomer.is_business" class="badge bg-success">Entreprise</span>
                      <span v-else class="badge bg-info">Particulier</span>
                    </p>
                    <p v-if="selectedCustomer.vat_number"><strong>N° TVA:</strong> {{ selectedCustomer.vat_number }}</p>
                    <p v-if="selectedCustomer.iban"><strong>IBAN:</strong> {{ selectedCustomer.iban }}</p>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="card">
                  <div class="card-header"><h6>Historique financier</h6></div>
                  <div class="card-body">
                    <p><strong>Solde dû:</strong> <span class="text-danger">€0.00</span></p>
                    <p><strong>Total facturé:</strong> €0.00</p>
                    <p><strong>Dernière commande:</strong> Aucune</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="row mt-3">
              <div class="col-12">
                <div class="card">
                  <div class="card-header"><h6>Commandes en cours</h6></div>
                  <div class="card-body">
                    <p class="text-muted">Aucune commande en cours</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="row mt-3">
              <div class="col-12">
                <div class="card">
                  <div class="card-header"><h6>Factures</h6></div>
                  <div class="card-body">
                    <p class="text-muted">Aucune facture</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal modification client -->
    <div class="modal fade" :class="{ show: showEditModal, 'd-block': showEditModal }" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Modifier le client</h5>
            <button type="button" class="btn-close" @click="closeAllModals"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateCustomer">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Prénom</label>
                    <input type="text" class="form-control" v-model="customerForm.first_name">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Nom</label>
                    <input type="text" class="form-control" v-model="customerForm.last_name">
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" v-model="customerForm.email" readonly>
              </div>
              <div class="mb-3">
                <label class="form-label">Téléphone</label>
                <input type="tel" class="form-control" v-model="customerForm.phone">
              </div>
              <div v-if="customerForm.is_business">
                <div class="mb-3">
                  <label class="form-label">Nom de l'entreprise</label>
                  <input type="text" class="form-control" v-model="customerForm.company_name">
                </div>
                <div class="mb-3">
                  <label class="form-label">Adresse de l'entreprise</label>
                  <textarea class="form-control" rows="3" v-model="customerForm.company_address"></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label">Numéro de TVA</label>
                  <input type="text" class="form-control" v-model="customerForm.vat_number">
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">IBAN</label>
                <input type="text" class="form-control" v-model="customerForm.iban">
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-danger" @click="confirmDelete">Supprimer</button>
                <button type="button" class="btn btn-secondary" @click="closeAllModals">Annuler</button>
                <button type="submit" class="btn btn-primary">Modifier</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal confirmation suppression -->
    <div class="modal fade" :class="{ show: showDeleteConfirm, 'd-block': showDeleteConfirm }" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirmer la suppression</h5>
            <button type="button" class="btn-close" @click="showDeleteConfirm = false"></button>
          </div>
          <div class="modal-body">
            <p>Êtes-vous sûr de vouloir supprimer ce client ?</p>
            <p class="text-danger"><strong>Cette action est irréversible.</strong></p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteConfirm = false">Annuler</button>
            <button type="button" class="btn btn-danger" @click="deleteCustomer">Supprimer définitivement</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal backdrop -->
    <div v-if="showCreateModal || showViewModal || showEditModal || showDeleteConfirm" class="modal-backdrop fade show" @click="closeAllModals"></div>
  </div>
</template>

<script>
export default {
  name: 'Customers',
  data() {
    return {
      customers: [],
      showCreateModal: false,
      showViewModal: false,
      showEditModal: false,
      showDeleteConfirm: false,
      showSuccessMessage: false,
      successMessage: '',
      selectedCustomer: null,
      vatNumber: '',
      vatValidating: false,
      vatResult: null,
      customerForm: {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        is_business: false,
        company_name: '',
        company_address: '',
        vat_number: '',
        iban: ''
      }
    }
  },
  methods: {
    async validateVAT() {
      if (!this.vatNumber) return
      
      console.log('Début validation TVA:', this.vatNumber)
      this.vatValidating = true
      this.vatResult = null
      
      try {
        console.log('Envoi requête à:', '/api/shop/validate-vat/')
        const response = await fetch('http://localhost:8000/api/shop/validate-vat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ vat_number: this.vatNumber })
        })
        
        console.log('Réponse reçue, status:', response.status)
        
        if (!response.ok) {
          console.error('Erreur HTTP:', response.status, response.statusText)
          throw new Error(`HTTP ${response.status}`)
        }
        
        const data = await response.json()
        console.log('Données reçues:', data)
        this.vatResult = data
        
        if (data.valid) {
          console.log('TVA valide, remplissage automatique')
          this.customerForm.is_business = true
          this.customerForm.vat_number = data.vat_number
          this.customerForm.company_name = data.company_name || ''
          this.customerForm.company_address = data.company_address || ''
        } else {
          console.log('TVA invalide:', data.error)
        }
      } catch (error) {
        console.error('Erreur complète:', error)
        this.vatResult = {
          valid: false,
          error: `Erreur: ${error.message}`
        }
      } finally {
        this.vatValidating = false
        console.log('Fin validation TVA')
      }
    },
    clearVatValidation() {
      this.vatResult = null
    },
    async updateCustomer() {
      try {
        const response = await fetch(`http://localhost:8000/api/shop/customers/${this.selectedCustomer.id}/`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            phone: this.customerForm.phone,
            company_name: this.customerForm.company_name,
            company_address: this.customerForm.company_address,
            vat_number: this.customerForm.vat_number,
            iban: this.customerForm.iban
          })
        })
        
        if (response.ok) {
          this.successMessage = 'Client modifié avec succès !'
          this.showSuccessMessage = true
          setTimeout(() => { this.showSuccessMessage = false }, 2000)
          this.closeAllModals()
          await this.fetchCustomers()
        } else {
          const error = await response.json()
          console.error('Erreur modification:', error)
        }
      } catch (error) {
        console.error('Erreur modification client:', error)
      }
    },
    async saveCustomer() {
      try {
        // Créer l'utilisateur et le client
        const response = await fetch('http://localhost:8000/api/shop/customers/create_customer/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.customerForm)
        })
        
        if (response.ok) {
          this.successMessage = 'Client créé avec succès !'
          this.showSuccessMessage = true
          setTimeout(() => {
            this.showSuccessMessage = false
          }, 2000)
          this.closeAllModals()
          await this.fetchCustomers()
        } else {
          const error = await response.json()
          console.error('Erreur détaillée:', error)
          
          let errorMessage = 'Erreur lors de la création:\n'
          if (typeof error === 'object') {
            for (const [field, messages] of Object.entries(error)) {
              if (Array.isArray(messages)) {
                errorMessage += `${field}: ${messages.join(', ')}\n`
              } else {
                errorMessage += `${field}: ${messages}\n`
              }
            }
          } else {
            errorMessage += error
          }
          alert(errorMessage)
        }
      } catch (error) {
        console.error('Error creating customer:', error)
        alert('Erreur lors de la création du client')
      }
    },
    openModal() {
      console.log('Ouverture du modal')
      this.showCreateModal = true
    },
    async fetchCustomers() {
      try {
        const response = await fetch('http://localhost:8000/api/shop/customers/')
        if (response.ok) {
          const data = await response.json()
          this.customers = data.results || data
          console.log('Clients chargés:', this.customers)
        }
      } catch (error) {
        console.error('Erreur lors du chargement des clients:', error)
      }
    },
    viewCustomer(customer) {
      this.selectedCustomer = customer
      this.showViewModal = true
    },
    editCustomer(customer) {
      this.selectedCustomer = customer
      this.customerForm = {
        first_name: customer.user?.first_name || '',
        last_name: customer.user?.last_name || '',
        email: customer.user_email,
        phone: customer.phone,
        is_business: customer.is_business,
        company_name: customer.company_name,
        company_address: customer.company_address,
        vat_number: customer.vat_number,
        iban: customer.iban
      }
      this.showEditModal = true
    },
    confirmDelete() {
      this.showDeleteConfirm = true
    },
    async deleteCustomer() {
      try {
        const response = await fetch(`http://localhost:8000/api/shop/customers/${this.selectedCustomer.id}/`, {
          method: 'DELETE'
        })
        if (response.ok) {
          this.successMessage = 'Client supprimé avec succès !'
          this.showSuccessMessage = true
          setTimeout(() => { this.showSuccessMessage = false }, 2000)
          this.closeAllModals()
          await this.fetchCustomers()
        }
      } catch (error) {
        console.error('Erreur suppression:', error)
      }
    },
    closeAllModals() {
      this.showCreateModal = false
      this.showViewModal = false
      this.showEditModal = false
      this.showDeleteConfirm = false
      this.selectedCustomer = null
      this.vatNumber = ''
      this.vatResult = null
      this.customerForm = {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        is_business: false,
        company_name: '',
        company_address: '',
        vat_number: '',
        iban: ''
      }
    },
    closeModal() {
      this.closeAllModals()
    }
  },
  mounted() {
    this.fetchCustomers()
  }
}
</script>

<style scoped>
.modal.show {
  display: block !important;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1040;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal {
  z-index: 1050;
}

.alert {
  border-radius: 8px;
  border: none;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
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