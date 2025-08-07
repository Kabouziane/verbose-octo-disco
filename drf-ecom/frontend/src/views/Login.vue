<template>
  <div class="login-container">
    <div class="row justify-content-center w-100">
      <div class="col-12 col-sm-8 col-md-6 col-lg-5 col-xl-4">
        <div class="card shadow">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <i class="fas fa-store fa-3x text-primary mb-3"></i>
              <h2>Connexion</h2>
              <p class="text-muted">E-commerce & Comptabilité</p>
              <div class="alert alert-info">
                <small>
                  <strong>Identifiants de test :</strong><br>
                  Utilisateur : karim<br>
                  Mot de passe : 123
                </small>
              </div>
            </div>
            
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label class="form-label">Nom d'utilisateur</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="credentials.username"
                  required
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">Mot de passe</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="credentials.password"
                  required
                >
              </div>
              
              <div v-if="error" class="alert alert-danger">
                {{ error }}
              </div>
              
              <button 
                type="submit" 
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Se connecter
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      credentials: {
        username: 'karim',
        password: '123'
      },
      loading: false,
      error: null
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = null
      
      try {
        await this.$store.dispatch('auth/login', this.credentials)
        this.$router.push('/dashboard')
      } catch (error) {
        this.error = 'Identifiants incorrects'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.card {
  border: none;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  min-width: 350px;
}

.form-control {
  border-radius: 10px;
  border: 2px solid #e9ecef;
  padding: 15px 18px;
  font-size: 16px;
  transition: all 0.3s ease;
  height: auto;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  padding: 15px 20px;
  font-weight: 600;
  font-size: 16px;
  transition: transform 0.2s ease;
  height: auto;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.text-primary {
  color: #667eea !important;
}

.alert {
  border-radius: 10px;
  border: none;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.card {
  animation: fadeIn 0.6s ease-out;
}
</style>