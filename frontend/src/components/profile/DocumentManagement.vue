<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Verification Documents</h5>
      <div v-if="!isUploadMode">
        <button class="btn btn-sm btn-outline-primary me-2" @click="handleDownload"
          :disabled="isDownloading || !hasDocuments">
          <i class="bi bi-download me-1"></i>
          {{ isDownloading ? 'Downloading...' : 'Download Document' }}
        </button>
        <button class="btn btn-sm btn-outline-success" @click="toggleUploadMode">
          <i class="bi bi-upload me-1"></i>
          Update Document
        </button>
      </div>
    </div>

    <div class="card-body p-4">
      <!-- Document Status -->
      <div v-if="!isUploadMode" class="document-status">
        <div class="mb-4">
          <div class="d-flex align-items-center">
            <div class="document-icon me-3">
              <i class="bi" :class="documentIcon"></i>
            </div>
            <div>
              <h6 class="mb-1">Current Verification Status</h6>
              <p class="mb-0" v-if="hasDocuments">
                <span class="badge me-2" :class="verificationStatusBadge">
                  <i class="bi me-1" :class="verificationStatusIcon"></i>
                  {{ verificationStatus }}
                </span>
                <small class="text-muted">
                  {{ documentName || 'Verification document uploaded' }}
                </small>
              </p>
              <p class="mb-0 text-muted" v-else>No verification document uploaded yet.</p>
            </div>
          </div>
        </div>

        <div class="alert alert-info" v-if="!isVerified && hasDocuments">
          <i class="bi bi-info-circle-fill me-2"></i>
          Your document is under review. You will be notified once it's verified.
        </div>

        <div class="alert alert-warning" v-if="!hasDocuments">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Please upload a verification document to provide your professional services.
        </div>
      </div>

      <!-- Upload Form -->
      <form v-if="isUploadMode" @submit.prevent="handleSubmit">
        <div class="alert alert-warning mb-4">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          <strong>Important:</strong> Updating your document will require re-verification by admin.
          You cannot accept new service requests until your document is verified.
        </div>

        <div class="mb-3">
          <label for="document" class="form-label">Verification Document</label>
          <div class="input-group">
            <input type="file" class="form-control" id="document" ref="documentInput"
              @change="handleFileChange" accept=".pdf,.jpg,.jpeg,.png"
              :class="{ 'is-invalid': validationError }" required />
            <button type="button" class="btn btn-outline-secondary" @click="clearSelection"
              v-if="selectedFile">
              <i class="bi bi-x"></i>
            </button>
            <div class="invalid-feedback">{{ validationError }}</div>
          </div>
          <div class="form-text">Accepted formats: PDF, JPG, JPEG, PNG. Maximum size: 5MB.</div>
        </div>

        <div v-if="selectedFile" class="mb-4">
          <div class="d-flex align-items-center p-3 border rounded bg-light">
            <i class="bi" :class="fileIcon"></i>
            <div class="ms-3">
              <div class="small fw-medium">{{ selectedFile.name }}</div>
              <div class="small text-muted">{{ formatFileSize(selectedFile.size) }}</div>
            </div>
          </div>
        </div>

        <div class="d-flex justify-content-end gap-2 mt-4">
          <button type="button" class="btn btn-outline-secondary" @click="cancelUpload">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="isUploading || !selectedFile">
            <span v-if="isUploading" class="spinner-border spinner-border-sm me-2"></span>
            {{ isUploading ? 'Uploading...' : 'Upload Document' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Navigation Guard for Unsaved Changes -->
    <FormNavigationGuard :when="hasUnsavedChanges"
      message="You have a document selected but not uploaded. Are you sure you want to leave?" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import router from '@/router';

export default {
  name: 'DocumentManagement',

  setup() {
    const store = useStore();
    const documentInput = ref(null);
    const selectedFile = ref(null);
    const validationError = ref('');
    const isUploadMode = ref(false);
    const isUploading = ref(false);
    const isDownloading = ref(false);
    const hasUnsavedChanges = ref(false);
    const documentName = ref('');

    // Get user data from store
    const userData = computed(() => store.getters['auth/currentUser']);
    const hasDocuments = computed(() => !!userData.value?.verification_documents);
    const isVerified = computed(() => !!userData.value?.is_verified);

    // Computed properties for UI state
    const verificationStatus = computed(() => {
      if (!hasDocuments.value) return 'No Document';
      return isVerified.value ? 'Verified' : 'Pending Verification';
    });

    const verificationStatusBadge = computed(() => {
      if (!hasDocuments.value) return 'bg-secondary';
      return isVerified.value ? 'bg-success' : 'bg-warning';
    });

    const verificationStatusIcon = computed(() => {
      if (!hasDocuments.value) return 'bi-x-circle';
      return isVerified.value ? 'bi-check-circle' : 'bi-hourglass-split';
    });

    const documentIcon = computed(() => {
      if (!hasDocuments.value) return 'bi-file-earmark-x text-secondary';
      return isVerified.value
        ? 'bi-file-earmark-check text-success'
        : 'bi-file-earmark-text text-warning';
    });

    const fileIcon = computed(() => {
      if (!selectedFile.value) return 'bi-file-earmark';

      const fileType = selectedFile.value.name.split('.').pop().toLowerCase();
      switch (fileType) {
        case 'pdf':
          return 'bi-file-earmark-pdf fs-4 text-danger';
        case 'jpg':
        case 'jpeg':
        case 'png':
          return 'bi-file-earmark-image fs-4 text-primary';
        default:
          return 'bi-file-earmark fs-4';
      }
    });

    // Format file size with appropriate units
    const formatFileSize = (bytes) => {
      if (bytes < 1024) return bytes + ' bytes';
      else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
      else return (bytes / 1048576).toFixed(1) + ' MB';
    };

    // Extract document name from path
    const extractDocumentName = (path) => {
      if (!path) return '';
      // Extract filename from path and decode if needed
      const filename = path.split('/').pop();
      return filename || '';
    };

    // Toggle upload mode
    const toggleUploadMode = () => {
      isUploadMode.value = true;
      selectedFile.value = null;
      validationError.value = '';
    };

    // Cancel upload and return to view mode
    const cancelUpload = () => {
      if (hasUnsavedChanges.value) {
        if (
          !confirm(
            'You have a document selected but not uploaded. Are you sure you want to cancel?',
          )
        ) {
          return;
        }
      }
      isUploadMode.value = false;
      selectedFile.value = null;
      validationError.value = '';
      hasUnsavedChanges.value = false;
    };

    // Clear file selection
    const clearSelection = () => {
      selectedFile.value = null;
      validationError.value = '';
      hasUnsavedChanges.value = false;

      // Reset the file input
      if (documentInput.value) {
        documentInput.value.value = '';
      }
    };

    // Handle file selection
    const handleFileChange = (event) => {
      const file = event.target.files[0];
      if (!file) {
        selectedFile.value = null;
        hasUnsavedChanges.value = false;
        return;
      }

      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
      if (!allowedTypes.includes(file.type)) {
        validationError.value = 'Invalid file type. Please upload a PDF, JPG, JPEG, or PNG file.';
        selectedFile.value = null;
        hasUnsavedChanges.value = false;
        return;
      }

      // Validate file size (max 5MB)
      const maxSize = 5 * 1024 * 1024; // 5MB in bytes
      if (file.size > maxSize) {
        validationError.value = 'File size exceeds the maximum limit of 5MB.';
        selectedFile.value = null;
        hasUnsavedChanges.value = false;
        return;
      }

      // Clear any previous errors and set the file
      validationError.value = '';
      selectedFile.value = file;
      hasUnsavedChanges.value = true;
    };

    // Handle form submission (document upload)
    const handleSubmit = async () => {
      if (!selectedFile.value) {
        validationError.value = 'Please select a file to upload.';
        return;
      }

      try {
        isUploading.value = true;

        // Create FormData with the correct field name expected by the backend
        const formData = new FormData();
        formData.append('verification_document', selectedFile.value);

        // Pass FormData directly to the action
        // The correct implementation would have the action accept FormData directly
        await store.dispatch('professionals/updateDocument', { data: formData });

        // Show success message
        window.showToast({
          type: 'success',
          title:
            'Your verification document has been uploaded successfully and is pending review.',
        });

        // Reset form and exit upload mode
        isUploadMode.value = false;
        selectedFile.value = null;
        hasUnsavedChanges.value = false;

        await store.dispatch('auth/logout');
        setTimeout(() => {
          router.push('/login');
        }, 100);
      }
      catch (error) {
        // Show error message
        window.showToast({
          type: 'error',
          title: error.response?.data?.detail || 'Failed to upload document. Please try again.',
        });

        // If error indicates active requests, show specific message
        if (error.response?.data?.error_type === 'ActiveRequestsExist') {
          validationError.value =
            'You have active service requests. Please complete them before updating your document.';
        } else {
          validationError.value =
            error.response?.data?.detail || 'Failed to upload document. Please try again.';
        }
      } finally {
        isUploading.value = false;
      }
    };

    // Handle document download
    const handleDownload = async () => {
      if (!hasDocuments.value) {
        window.showToast({
          type: 'warning',
          title: 'You do not have any verification document to download.',
        });
        return;
      }

      try {
        isDownloading.value = true;

        // Download document
        const response = await store.dispatch('professionals/downloadDocument');

        // Create download link
        const blob = new Blob([response.data], {
          type: response.headers['content-type'],
        });
        const url = window.URL.createObjectURL(blob);

        // Get filename from Content-Disposition header or use default
        let filename = 'verification_document';
        const contentDisposition = response.headers['content-disposition'];
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
          if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1];
          }
        }

        // Add file extension if missing
        if (!filename.includes('.')) {
          const contentType = response.headers['content-type'];
          if (contentType.includes('pdf')) filename += '.pdf';
          else if (contentType.includes('jpeg') || contentType.includes('jpg')) filename += '.jpg';
          else if (contentType.includes('png')) filename += '.png';
          else filename += '.pdf'; // Default to PDF
        }

        // Create and trigger download link
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();

        // Clean up URL object
        window.URL.revokeObjectURL(url);

        // Show success message
        window.showToast({
          type: 'success',
          title: 'Your document download has started.',
        });
      } catch (error) {
        // Show error message
        window.showToast({
          type: 'error',
          title: error.response?.data?.detail || 'Failed to download document. Please try again.',
        });
      } finally {
        isDownloading.value = false;
      }
    };

    // Initialize on component mount
    onMounted(() => {
      if (hasDocuments.value) {
        documentName.value = extractDocumentName(userData.value?.verification_documents);
      }
    });

    return {
      documentInput,
      selectedFile,
      validationError,
      isUploadMode,
      isUploading,
      isDownloading,
      hasUnsavedChanges,
      documentName,
      hasDocuments,
      isVerified,
      verificationStatus,
      verificationStatusBadge,
      verificationStatusIcon,
      documentIcon,
      fileIcon,
      formatFileSize,
      toggleUploadMode,
      cancelUpload,
      clearSelection,
      handleFileChange,
      handleSubmit,
      handleDownload,
    };
  },
};
</script>

<style scoped>
.document-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background-color: #f8f9fa;
  border-radius: 50%;
}

.document-icon i {
  font-size: 1.5rem;
}

.alert {
  border-left: 4px solid;
}

.alert-info {
  border-left-color: var(--bs-info);
}

.alert-warning {
  border-left-color: var(--bs-warning);
}

.badge {
  font-weight: 500;
}
</style>
