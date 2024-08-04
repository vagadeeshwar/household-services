<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-4">
        <div class="card mt-5">
          <div class="card-body">
            <h2 class="card-title text-center">User Login</h2>
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
export default {
  data() {
    return {
      username: '',
      password: '',
    };
  },
  methods: {
    handleSubmit() {
      // Add login logic here
      alert('Login submitted');
    },
    goToRegister() {
      this.$router.push('/register');
    },
  },
};
</script>

<style scoped>
.card-title {
  margin-bottom: 1rem;
}
</style>
