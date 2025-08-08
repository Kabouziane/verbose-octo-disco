<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Tableau de bord</h1>
      <div class="btn-toolbar mb-2 mb-md-0">
        <div class="btn-group me-2">
          <button type="button" class="btn btn-sm btn-outline-secondary">Exporter</button>
        </div>
      </div>
    </div>

    <!-- Statistiques -->
    <div class="row mb-4">
      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Clients</div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.customers }}</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-users fa-2x text-gray-300"></i>
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
                <div class="text-xs font-weight-bold text-success text-uppercase mb-1">Commandes</div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.orders }}</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-shopping-cart fa-2x text-gray-300"></i>
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
                <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Produits</div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.products }}</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-box fa-2x text-gray-300"></i>
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
                <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Chiffre d'affaires</div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">€{{ stats.revenue }}</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-euro-sign fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Activité récente -->
    <div class="row">
      <div class="col-lg-6">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Dernières commandes</h6>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>N°</th>
                    <th>Client</th>
                    <th>Montant</th>
                    <th>Statut</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>#001</td>
                    <td>Jean Dupont</td>
                    <td>€125.50</td>
                    <td><span class="badge bg-success">Livrée</span></td>
                  </tr>
                  <tr>
                    <td>#002</td>
                    <td>Marie Martin</td>
                    <td>€89.90</td>
                    <td><span class="badge bg-warning">En cours</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Nouveaux clients</h6>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Nom</th>
                    <th>Email</th>
                    <th>Type</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="customer in recentCustomers" :key="customer.id">
                    <td>{{ customer.full_name || customer.company_name }}</td>
                    <td>{{ customer.user_email }}</td>
                    <td>
                      <span v-if="customer.is_business" class="badge bg-success">Entreprise</span>
                      <span v-else class="badge bg-info">Particulier</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        customers: 0,
        orders: 0,
        products: 0,
        revenue: '0.00'
      },
      recentCustomers: []
    }
  },
  async mounted() {
    await this.loadStats()
    await this.loadRecentCustomers()
  },
  methods: {
    async loadStats() {
      try {
        const response = await fetch('http://localhost:8000/api/shop/customers/')
        if (response.ok) {
          const data = await response.json()
          this.stats.customers = data.count || (data.results ? data.results.length : 0)
        }
      } catch (error) {
        console.error('Erreur chargement stats:', error)
      }
    },
    async loadRecentCustomers() {
      try {
        const response = await fetch('http://localhost:8000/api/shop/customers/')
        if (response.ok) {
          const data = await response.json()
          const customers = data.results || data
          this.recentCustomers = customers.slice(0, 3)
        }
      } catch (error) {
        console.error('Erreur chargement clients récents:', error)
      }
    }
  }
}
</script>

<style scoped>
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

.text-xs {
  font-size: 0.7rem;
}

.text-gray-300 {
  color: #dddfeb !important;
}

.text-gray-800 {
  color: #5a5c69 !important;
}

.shadow {
  box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;
}
</style>