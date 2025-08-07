<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Dashboard</h1>
    </div>

    <!-- Statistiques -->
    <div class="row mb-4">
      <div class="col-xl-3 col-md-6 mb-4">
        <div class="card border-left-primary shadow h-100 py-2">
          <div class="card-body">
            <div class="row no-gutters align-items-center">
              <div class="col mr-2">
                <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                  Chiffre d'affaires (Mensuel)
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">€40,000</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-euro-sign fa-2x text-gray-300"></i>
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
                  Commandes
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">215</div>
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
                <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                  Clients
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">156</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-users fa-2x text-gray-300"></i>
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
                  Factures en attente
                </div>
                <div class="h5 mb-0 font-weight-bold text-gray-800">18</div>
              </div>
              <div class="col-auto">
                <i class="fas fa-file-invoice fa-2x text-gray-300"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Graphiques -->
    <div class="row">
      <div class="col-xl-8 col-lg-7">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Évolution du chiffre d'affaires</h6>
          </div>
          <div class="card-body">
            <canvas id="salesChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <div class="col-xl-4 col-lg-5">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Répartition TVA</h6>
          </div>
          <div class="card-body">
            <canvas id="vatChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Dernières activités -->
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
                    <td>#CMD001</td>
                    <td>Jean Dupont</td>
                    <td>€125.50</td>
                    <td><span class="badge bg-success">Payée</span></td>
                  </tr>
                  <tr>
                    <td>#CMD002</td>
                    <td>Marie Martin</td>
                    <td>€89.90</td>
                    <td><span class="badge bg-warning">En attente</span></td>
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
            <h6 class="m-0 font-weight-bold text-primary">Dernières factures</h6>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>N°</th>
                    <th>Client</th>
                    <th>Montant</th>
                    <th>Échéance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>FAC2024001</td>
                    <td>Entreprise ABC</td>
                    <td>€1,250.00</td>
                    <td>15/01/2024</td>
                  </tr>
                  <tr>
                    <td>FAC2024002</td>
                    <td>Société XYZ</td>
                    <td>€890.50</td>
                    <td>20/01/2024</td>
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
  mounted() {
    this.initCharts()
  },
  methods: {
    initCharts() {
      // Graphique des ventes
      const salesCtx = document.getElementById('salesChart').getContext('2d')
      new Chart(salesCtx, {
        type: 'line',
        data: {
          labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
          datasets: [{
            label: 'Chiffre d\'affaires',
            data: [12000, 19000, 15000, 25000, 22000, 30000],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
          }]
        }
      })

      // Graphique TVA
      const vatCtx = document.getElementById('vatChart').getContext('2d')
      new Chart(vatCtx, {
        type: 'doughnut',
        data: {
          labels: ['TVA 21%', 'TVA 6%', 'TVA 0%'],
          datasets: [{
            data: [65, 25, 10],
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
          }]
        }
      })
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
</style>