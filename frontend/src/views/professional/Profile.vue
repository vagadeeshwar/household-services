<template>
  <div class="container py-5">
    <div class="row justify-content-center g-4">
      <!-- Profile Information -->
      <div class="col-lg-8">
        <ProfileInfo />
      </div>

      <!-- Document Management for professionals only -->
      <div class="col-lg-8">
        <DocumentManagement />
      </div>

      <!-- Password Management -->
      <div class="col-lg-8">
        <PasswordChangeForm />
      </div>

      <!-- Account Deletion -->
      <div class="col-lg-8">
        <AccountDeleteForm />
      </div>

      <div class="col-lg-8">
        <ActivityLogs />
      </div>
    </div>
  </div>
</template>
<script>
import ProfileInfo from '@/components/profile/ProfileInfo.vue'
import PasswordChangeForm from '@/components/profile/PasswordChangeForm.vue'
import AccountDeleteForm from '@/components/profile/AccountDeleteForm.vue'
import DocumentManagement from '@/components/profile/DocumentManagement.vue'
import ActivityLogs from '@/components/profile/ActivityLogs.vue'
export default {
  name: 'ProfessionalProfile',
  components: {
    ProfileInfo,
    PasswordChangeForm,
    AccountDeleteForm,
    DocumentManagement,
    ActivityLogs,
  },
}
</script>
<style scoped>
.container {
  max-width: 900px;
}
</style>
