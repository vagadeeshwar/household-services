<template>
  <div class="container py-5">
    <div class="row justify-content-center g-4">
      <!-- Profile Information -->
      <div class="col-lg-8">
        <ProfileInfo />
      </div>

      <!-- Password Management -->
      <div class="col-lg-8">
        <PasswordChangeForm />
      </div>

      <!-- Account Deletion -->
      <div class="col-lg-8">
        <AccountDeleteForm />
      </div>
    </div>
  </div>
</template>

<script>
import ProfileInfo from '@/components/profile/ProfileInfo.vue'
import PasswordChangeForm from '@/components/profile/PasswordChangeForm.vue'
import AccountDeleteForm from '@/components/profile/AccountDeleteForm.vue'

export default {
  name: 'CustomerProfile',
  components: {
    ProfileInfo,
    PasswordChangeForm,
    AccountDeleteForm,
  },
}
</script>

<style scoped>
.container {
  max-width: 900px;
}
</style>
