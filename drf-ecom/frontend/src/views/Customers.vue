<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Clients</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="fas fa-plus me-2"></i>Nouveau client
      </button>
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
              <tr>
                <td><strong>Jean Dupont</strong></td>
                <td>jean@example.com</td>
                <td>+32 123 456 789</td>
                <td><span class="badge bg-info">Particulier</span></td>
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

    <!-- Modal création client -->
    <div class="modal fade" :class="{ show: showCreateModal }" :style="{ display: showCreateModal ? 'block' : 'none' }">
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
                    <label class="form-label">Prénom *</label>
                    <input type="text" class="form-control" v-model="customerForm.first_name" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Nom *</label>
                    <input type="text" class="form-control" v-model="customerForm.last_name" required>
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
                  <label class="form-label">Nom de l'entreprise</label>
                  <input type="text" class="form-control" v-model="customerForm.company_name">
                </div>
                <div class="mb-3">
                  <label class="form-label">Numéro de TVA</label>
                  <input type="text" class="form-control" v-model="customerForm.vat_number">
                </div>
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
  </div>
</template>

<script>
export default {
  name: 'Customers',
  data() {
    return {
      showCreateModal: false,
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
        vat_number: ''
      }
    }
  },
  methods: {
    async validateVAT() {
      if (!this.vatNumber) return
      
      this.vatValidating = true
      this.vatResult = null
      
      try {
        const response = await fetch('/api/shop/customers/validate_vat/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ vat_number: this.vatNumber })
        })
        
        const data = await response.json()
        this.vatResult = data
        
        if (data.valid) {
          // Remplir automatiquement le formulaire
          this.customerForm.is_business = true
          this.customerForm.vat_number = data.vat_number
          this.customerForm.company_name = data.company_name || ''
          
          // Si on a une adresse, on peut pré-remplir d'autres champs
          if (data.company_address) {
            // Logique pour parser l'adresse si nécessaire
          }
        }
      } catch (error) {
        console.error('Error validating VAT:', error)
        this.vatResult = {
          valid: false,
          error: 'Erreur lors de la vérification'
        }
      } finally {
        this.vatValidating = false
      }
    },
    clearVatValidation() {
      this.vatResult = null
    },
    async saveCustomer() {
      try {
        // Créer l'utilisateur et le client
        const response = await fetch('/api/shop/customers/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.customerForm)
        })
        
        if (response.ok) {
          this.closeModal()
          // Recharger la liste des clients
          this.fetchCustomers()
        } else {
          const error = await response.json()
          alert('Erreur lors de la création: ' + JSON.stringify(error))
        }
      } catch (error) {
        console.error('Error creating customer:', error)
        alert('Erreur lors de la création du client')
      }
    },
    fetchCustomers() {
      // Méthode pour recharger la liste
      console.log('Fetching customers...')
    },
    closeModal() {
      this.showCreateModal = false
      this.vatNumber = ''
      this.vatResult = null
      this.customerForm = {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        is_business: false,
        company_name: '',
        vat_number: ''
      }
    }
  }
}
</script>

<style scoped>
.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.alert {
  border-radius: 8px;
  border: none;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}
</style>