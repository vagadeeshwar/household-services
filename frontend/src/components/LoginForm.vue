<template>
    <div class="container mt-5">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card">
            <div class="card-body">
              <h2 class="text-center mb-4">User Login</h2>
              <form @submit.prevent="handleSubmit">
                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input type="text" id="username" v-model="username" class="form-control" required />
                </div>
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input type="password" id="password" v-model="password" class="form-control" required />
                </div>
                <div class="d-flex justify-content-between">
                  <button type="submit" class="btn btn-primary">Login</button>
                  <button @click="goToRegister" type="button" class="btn btn-secondary">Register</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  
  export default {
    setup() {
      const username = ref('');
      const password = ref('');
      const router = useRouter();
  
      const handleSubmit = () => {
        // Add login logic here
        alert('Login submitted');
      };
  
      const goToRegister = () => {
        router.push('/register');
      };
  
      return {
        username,
        password,
        handleSubmit,
        goToRegister,
      };
    },
  };
  </script>
  