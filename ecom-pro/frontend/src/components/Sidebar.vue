<template>
  <nav id="sidebarMenu" class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse">
    <div class="position-sticky pt-3">
      <ul class="nav flex-column">
        <li class="nav-item">
          <router-link class="nav-link" to="/dashboard">
            <i class="fas fa-tachometer-alt me-2"></i>Dashboard
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/products">
            <i class="fas fa-box me-2"></i>Produits
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/orders">
            <i class="fas fa-shopping-cart me-2"></i>Commandes
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/customers">
            <i class="fas fa-users me-2"></i>Clients
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/invoices">
            <i class="fas fa-file-invoice me-2"></i>Factures
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/accounting">
            <i class="fas fa-calculator me-2"></i>Comptabilité
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/vat">
            <i class="fas fa-percentage me-2"></i>TVA
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/services">
            <i class="fas fa-cogs me-2"></i>Services
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" to="/appointments">
            <i class="fas fa-calendar me-2"></i>Rendez-vous
          </router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Sidebar'
}
</script>

<style scoped>
.nav-link {
  color: #333;
}

.nav-link:hover {
  color: #007bff;
}

.router-link-active {
  color: #007bff !important;
  background-color: rgba(0, 123, 255, 0.1);
}
</style>