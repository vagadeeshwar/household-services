<template>
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-4">
          <div class="card mt-5">
            <div class="card-body">
              <h2 class="card-title text-center">Register</h2>
              <form>
                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input type="text" id="username" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input type="password" id="password" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">Confirm Password</label>
                  <input type="password" id="confirmPassword" class="form-control" required />
                </div>
                <button type="submit" class="btn btn-primary w-100">Register</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
  };
  </script>
  
  <style scoped>
  .card-title {
    margin-bottom: 1rem;
  }
  </style>
  