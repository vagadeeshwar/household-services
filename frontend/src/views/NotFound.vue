<template>
    <div class="container text-center mt-5">
      <h2>Page Not Found</h2>
      <button @click="goHome" class="btn btn-primary mt-3">Go to Home</button>
    </div>
  </template>
  
  <script>
  import { useRouter } from 'vue-router';
  
  export default {
    setup() {
      const router = useRouter();
  
      const goHome = () => {
        router.push('/');
      };
  
      return {
        goHome,
      };
    },
  };
  </script>
  