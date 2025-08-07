<template>
  <div>
    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
      <h1 class="h2">Services</h1>
    </div>

    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Type</th>
                <th>Prix</th>
                <th>Durée</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Consultation IT</strong></td>
                <td><span class="badge bg-primary">Consultation</span></td>
                <td>€75.00/h</td>
                <td>1h</td>
                <td><span class="badge bg-success">Actif</span></td>
                <td>
                  <button class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-edit"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Services'
}
</script>