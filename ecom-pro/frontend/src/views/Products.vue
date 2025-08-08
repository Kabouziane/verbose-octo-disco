<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Produits</h1>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <i class="fas fa-plus me-2"></i>Nouveau produit
      </button>
    </div>

    <!-- Filtres -->
    <div class="row mb-3">
      <div class="col-md-4">
        <input 
          type="text" 
          class="form-control" 
          placeholder="Rechercher un produit..."
          v-model="searchTerm"
        >
      </div>
      <div class="col-md-3">
        <select class="form-select" v-model="selectedCategory">
          <option value="">Toutes les catégories</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Liste des produits -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status"></div>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Image</th>
                <th>Nom</th>
                <th>Catégorie</th>
                <th>Prix HT</th>
                <th>Prix TTC</th>
                <th>Stock</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredProducts" :key="product.id">
                <td>
                  <img 
                    :src="product.images?.[0]?.image || '/placeholder.jpg'" 
                    alt="Product" 
                    class="product-image"
                  >
                </td>
                <td>
                  <strong>{{ product.name }}</strong>
                  <br>
                  <small class="text-muted">{{ product.sku }}</small>
                </td>
                <td>{{ product.category_name }}</td>
                <td>€{{ product.price }}</td>
                <td>€{{ product.price_with_vat }}</td>
                <td>
                  <span :class="stockClass(product.stock_quantity)">
                    {{ product.stock_quantity }}
                  </span>
                </td>
                <td>
                  <span :class="product.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ product.is_active ? 'Actif' : 'Inactif' }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="editProduct(product)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="deleteProduct(product)">
                    <i class="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal création/édition -->
    <div class="modal fade" :class="{ show: showCreateModal }" :style="{ display: showCreateModal ? 'block' : 'none' }">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingProduct ? 'Modifier' : 'Nouveau' }} produit</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveProduct">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Nom du produit</label>
                    <input type="text" class="form-control" v-model="productForm.name" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">SKU</label>
                    <input type="text" class="form-control" v-model="productForm.sku" required>
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" rows="3" v-model="productForm.description"></textarea>
              </div>
              
              <div class="row">
                <div class="col-md-4">
                  <div class="mb-3">
                    <label class="form-label">Prix HT</label>
                    <input type="number" step="0.01" class="form-control" v-model="productForm.price" required>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label class="form-label">Taux TVA (%)</label>
                    <select class="form-select" v-model="productForm.vat_rate">
                      <option value="21">21%</option>
                      <option value="6">6%</option>
                      <option value="0">0%</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label class="form-label">Stock</label>
                    <input type="number" class="form-control" v-model="productForm.stock_quantity" required>
                  </div>
                </div>
              </div>
              
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">Annuler</button>
                <button type="submit" class="btn btn-primary">Enregistrer</button>
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
  name: 'Products',
  data() {
    return {
      searchTerm: '',
      selectedCategory: '',
      showCreateModal: false,
      editingProduct: null,
      productForm: {
        name: '',
        sku: '',
        description: '',
        price: '',
        vat_rate: 21,
        stock_quantity: 0
      }
    }
  },
  computed: {
    ...mapState('products', ['products', 'categories', 'loading']),
    filteredProducts() {
      return this.products.filter(product => {
        const matchesSearch = product.name.toLowerCase().includes(this.searchTerm.toLowerCase())
        const matchesCategory = !this.selectedCategory || product.category === parseInt(this.selectedCategory)
        return matchesSearch && matchesCategory
      })
    }
  },
  methods: {
    ...mapActions('products', ['fetchProducts', 'fetchCategories']),
    stockClass(quantity) {
      if (quantity === 0) return 'badge bg-danger'
      if (quantity < 10) return 'badge bg-warning'
      return 'badge bg-success'
    },
    editProduct(product) {
      this.editingProduct = product
      this.productForm = { ...product }
      this.showCreateModal = true
    },
    deleteProduct(product) {
      if (confirm('Êtes-vous sûr de vouloir supprimer ce produit ?')) {
        // API call to delete
        console.log('Delete product:', product.id)
      }
    },
    saveProduct() {
      // API call to save
      console.log('Save product:', this.productForm)
      this.closeModal()
    },
    closeModal() {
      this.showCreateModal = false
      this.editingProduct = null
      this.productForm = {
        name: '',
        sku: '',
        description: '',
        price: '',
        vat_rate: 21,
        stock_quantity: 0
      }
    }
  },
  mounted() {
    this.fetchProducts()
    this.fetchCategories()
  }
}
</script>

<style scoped>
.product-image {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 5px;
}

.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>