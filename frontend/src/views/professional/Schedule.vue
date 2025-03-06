<template>
  <div class="container py-4">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col">
        <h1 class="h3 mb-2">My Schedule</h1>
        <p class="text-muted">Manage your appointments and upcoming services</p>
      </div>
      <div class="col-auto">
        <div class="d-flex align-items-center">
          <div class="form-check form-switch me-3">
            <input class="form-check-input" type="checkbox" id="showCompleted"
              v-model="showCompleted">
            <label class="form-check-label" for="showCompleted">Show Completed</label>
          </div>
          <button class="btn btn-primary" @click="refreshSchedule">
            <i class="bi bi-arrow-clockwise me-2"></i>Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading your schedule...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
      <button @click="loadSchedule" class="btn btn-sm btn-outline-danger ms-2">
        Retry
      </button>
    </div>

    <!-- Schedule Content -->
    <div v-else class="row">
      <!-- Calendar Column -->
      <div class="col-lg-9">
        <div class="card shadow-sm">
          <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Schedule Calendar</h5>
            <div class="btn-group">
              <button class="btn btn-sm btn-outline-secondary" @click="prevWeek">
                <i class="bi bi-chevron-left"></i>
              </button>
              <button class="btn btn-sm btn-outline-secondary" @click="todayWeek">
                Today
              </button>
              <button class="btn btn-sm btn-outline-secondary" @click="nextWeek">
                <i class="bi bi-chevron-right"></i>
              </button>
            </div>
          </div>
          <div class="card-body p-0">
            <!-- Week View -->
            <div class="table-responsive">
              <table class="table table-bordered mb-0">
                <thead>
                  <tr>
                    <th class="time-column"></th>
                    <th v-for="(day, index) in weekDays" :key="index" class="text-center"
                      :class="{ 'today': isToday(day.date) }">
                      <div class="day-header">
                        <div class="day-name">{{ formatDayName(day.date) }}</div>
                        <div class="day-date">{{ formatDayDate(day.date) }}</div>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="hour in displayHours" :key="hour">
                    <td class="time-column">
                      <div class="hour-label">{{ formatHourLabel(hour) }}</div>
                    </td>
                    <td v-for="(day, dayIndex) in weekDays" :key="`${dayIndex}-${hour}`"
                      class="schedule-cell" :class="{ 'today': isToday(day.date) }">
                      <!-- Service Appointments -->
                      <template v-for="(event, eventIndex) in getEventsForHour(day.date, hour)"
                        :key="eventIndex">
                        <div class="appointment-card" :class="getAppointmentClass(event)"
                          :style="getAppointmentStyle(event)"
                          @click="viewAppointmentDetails(event)">
                          <div class="appointment-time">{{ formatAppointmentTime(event) }}</div>
                          <div class="appointment-title">{{ event.service.name }}</div>
                          <div class="appointment-customer text-truncate">{{
                            event.customer.user.full_name }}</div>
                        </div>
                      </template>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Today's Appointments Column -->
      <div class="col-lg-3 mt-4 mt-lg-0">
        <div class="card shadow-sm">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Today's Appointments</h5>
          </div>
          <div class="card-body p-0">
            <!-- Empty State -->
            <div v-if="todayAppointments.length === 0" class="text-center py-5">
              <i class="bi bi-calendar-check text-muted fs-1 mb-3 d-block"></i>
              <p class="text-muted mb-0">No appointments scheduled for today</p>
            </div>
            <!-- Appointments List -->
            <div v-else class="list-group list-group-flush">
              <div v-for="(appointment, index) in todayAppointments" :key="index"
                class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <span class="badge" :class="getStatusBadgeClass(appointment.status)">
                      {{ formatTimeSlot(appointment.preferred_time,
                        appointment.service.estimated_time) }}
                    </span>
                  </div>
                  <button class="btn btn-sm btn-outline-primary"
                    @click="viewAppointmentDetails(appointment)">
                    <i class="bi bi-eye"></i>
                  </button>
                </div>
                <h6 class="mt-2 mb-1">{{ appointment.service.name }}</h6>
                <div class="d-flex align-items-center small text-muted">
                  <i class="bi bi-person me-1"></i>
                  <span>{{ appointment.customer.user.full_name }}</span>
                </div>
                <div class="d-flex align-items-center small text-muted mt-1">
                  <i class="bi bi-geo-alt me-1"></i>
                  <span class="text-truncate">{{ appointment.customer.user.address }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Appointments Card -->
        <div class="card shadow-sm mt-4">
          <div class="card-header bg-white py-3">
            <h5 class="mb-0">Upcoming Appointments</h5>
          </div>
          <div class="card-body p-0">
            <!-- Empty State -->
            <div v-if="upcomingAppointments.length === 0" class="text-center py-5">
              <i class="bi bi-calendar-date text-muted fs-1 mb-3 d-block"></i>
              <p class="text-muted mb-0">No upcoming appointments scheduled</p>
            </div>
            <!-- Appointments List -->
            <div v-else class="list-group list-group-flush">
              <div v-for="(appointment, index) in upcomingAppointments" :key="index"
                class="list-group-item">
                <div class="small text-muted mb-1">{{ formatUpcomingDate(appointment.preferred_time)
                  }}
                </div>
                <h6 class="mb-1">{{ appointment.service.name }}</h6>
                <div class="d-flex align-items-center small text-muted">
                  <i class="bi bi-person me-1"></i>
                  <span>{{ appointment.customer.user.full_name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointment Detail Modal -->
    <div class="modal fade" id="appointmentDetailModal" tabindex="-1" ref="appointmentDetailModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedAppointment">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"
              aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <!-- Service Details -->
              <div class="col-md-7">
                <div class="card h-100">
                  <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Service Information</h6>
                    <span class="badge" :class="getStatusBadgeClass(selectedAppointment.status)">
                      {{ formatStatus(selectedAppointment.status) }}
                    </span>
                  </div>
                  <div class="card-body">
                    <h5>{{ selectedAppointment.service.name }}</h5>
                    <p class="text-muted">{{ selectedAppointment.service.description }}</p>

                    <div class="row g-3 mt-2">
                      <div class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-clock text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Schedule Time</div>
                            <div>{{ formatDateLong(selectedAppointment.preferred_time) }}</div>
                          </div>
                        </div>
                      </div>
                      <div class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-hourglass-split text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Duration</div>
                            <div>{{ formatDuration(selectedAppointment.service.estimated_time) }}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-currency-rupee text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Price</div>
                            <div>₹{{ selectedAppointment.service.base_price }}</div>
                          </div>
                        </div>
                      </div>
                      <div class="col-sm-6">
                        <div class="d-flex align-items-center">
                          <i class="bi bi-calendar-date text-primary me-2 fs-5"></i>
                          <div>
                            <div class="small text-muted">Request Date</div>
                            <div>{{ formatDateOnly(selectedAppointment.date_of_request) }}</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="mt-4">
                      <h6>Request Description</h6>
                      <p>{{ selectedAppointment.description || 'No additional details provided.' }}
                      </p>
                    </div>

                    <div v-if="selectedAppointment.remarks" class="mt-4">
                      <h6>Completion Remarks</h6>
                      <p>{{ selectedAppointment.remarks }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Customer Details -->
              <div class="col-md-5">
                <div class="card h-100">
                  <div class="card-header">
                    <h6 class="mb-0">Customer Information</h6>
                  </div>
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-4">
                      <div class="avatar-circle bg-light text-primary me-3">
                        <i class="bi bi-person-fill"></i>
                      </div>
                      <div>
                        <h6 class="mb-0">{{ selectedAppointment.customer.user.full_name }}</h6>
                        <p class="text-muted mb-0 small">Customer</p>
                      </div>
                    </div>

                    <div class="mb-3">
                      <div class="small text-muted mb-1">Contact Details</div>
                      <div class="d-flex align-items-center mb-2">
                        <i class="bi bi-envelope me-2 text-muted"></i>
                        <span>{{ selectedAppointment.customer.user.email }}</span>
                      </div>
                      <div class="d-flex align-items-center">
                        <i class="bi bi-telephone me-2 text-muted"></i>
                        <span>{{ formatPhone(selectedAppointment.customer.user.phone) }}</span>
                      </div>
                    </div>

                    <div>
                      <div class="small text-muted mb-1">Service Location</div>
                      <div class="d-flex align-items-center">
                        <i class="bi bi-geo-alt me-2 text-muted"></i>
                        <span>{{ selectedAppointment.customer.user.address }}</span>
                      </div>
                      <div class="mt-2 d-flex align-items-center">
                        <i class="bi bi-pin-map me-2 text-muted"></i>
                        <span>PIN: {{ selectedAppointment.customer.user.pin_code }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button v-if="selectedAppointment.status === 'assigned'" type="button"
              class="btn btn-success" @click="completeAppointment" :disabled="isProcessing">
              <span v-if="isProcessing" class="spinner-border spinner-border-sm me-1"></span>
              Mark as Completed
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Appointment Modal -->
    <div class="modal fade" id="completeAppointmentModal" tabindex="-1"
      ref="completeAppointmentModal">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedAppointment">
          <div class="modal-header">
            <h5 class="modal-title">Complete Service</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"
              aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitCompletion">
              <div class="mb-3">
                <label for="completionRemarks" class="form-label">Service Remarks <span
                    class="text-danger">*</span></label>
                <textarea id="completionRemarks" class="form-control" v-model="completionRemarks"
                  rows="4" placeholder="Please provide details about the service completed..."
                  :class="{ 'is-invalid': remarksError }" required></textarea>
                <div class="invalid-feedback" v-if="remarksError">
                  {{ remarksError }}
                </div>
                <div class="form-text">
                  Include important details about the work performed, materials used, and any
                  follow-up
                  recommendations.
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-success" @click="submitCompletion"
              :disabled="isProcessing">
              <span v-if="isProcessing" class="spinner-border spinner-border-sm me-1"></span>
              Complete Service
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import moment from 'moment';
import * as bootstrap from 'bootstrap';

export default {
  name: 'ProfessionalSchedule',
  setup() {
    const store = useStore();

    // Refs for modals
    const appointmentDetailModal = ref(null);
    const completeAppointmentModal = ref(null);
    let bsAppointmentDetailModal = null;
    let bsCompleteAppointmentModal = null;

    // State
    const isLoading = ref(true);
    const error = ref(null);
    const showCompleted = ref(false);
    const appointments = ref([]);
    const currentWeekStart = ref(moment().startOf('week'));
    const selectedAppointment = ref(null);
    const completionRemarks = ref('');
    const remarksError = ref('');
    const isProcessing = ref(false);

    // Computed properties
    const weekDays = computed(() => {
      const days = [];
      for (let i = 0; i < 7; i++) {
        days.push({
          date: moment(currentWeekStart.value).add(i, 'days').toDate()
        });
      }
      return days;
    });

    const displayHours = computed(() => {
      // Business hours from 9 AM to 6 PM
      const hours = [];
      for (let i = 9; i <= 17; i++) {
        hours.push(i);
      }
      return hours;
    });

    const todayAppointments = computed(() => {
      const today = moment().startOf('day');
      return appointments.value
        .filter(app => {
          const appDate = moment(app.preferred_time).startOf('day');
          return appDate.isSame(today) && (showCompleted.value || app.status !== 'completed');
        })
        .sort((a, b) => moment(a.preferred_time).diff(moment(b.preferred_time)));
    });

    const upcomingAppointments = computed(() => {
      const today = moment().startOf('day');
      // eslint-disable-next-line no-unused-vars
      const tomorrow = moment().add(1, 'day').startOf('day');

      return appointments.value
        .filter(app => {
          const appDate = moment(app.preferred_time).startOf('day');
          return appDate.isAfter(today) && app.status !== 'completed';
        })
        .sort((a, b) => moment(a.preferred_time).diff(moment(b.preferred_time)))
        .slice(0, 5); // Show only next 5 upcoming appointments
    });

    // Methods
    const loadSchedule = async () => {
      isLoading.value = true;
      error.value = null;

      try {
        // Get start and end dates for fetching
        const startDate = moment(currentWeekStart.value).format('YYYY-MM-DD');
        const endDate = moment(currentWeekStart.value).add(6, 'days').format('YYYY-MM-DD');

        // Get requests for the current professional (both assigned and completed)
        const response = await store.dispatch('requests/fetchProfessionalRequests', {
          type: 'all',  // Get all requests
          startDate,
          endDate,
          perPage: 100  // Get a larger number to cover the week
        });

        appointments.value = response.data || [];
      } catch (err) {
        console.error('Error loading schedule:', err);
        error.value = 'Failed to load your schedule. Please try again.';
      } finally {
        isLoading.value = false;
      }
    };

    const refreshSchedule = () => {
      loadSchedule();
    };

    const prevWeek = () => {
      currentWeekStart.value = moment(currentWeekStart.value).subtract(1, 'week');
      loadSchedule();
    };

    const nextWeek = () => {
      currentWeekStart.value = moment(currentWeekStart.value).add(1, 'week');
      loadSchedule();
    };

    const todayWeek = () => {
      currentWeekStart.value = moment().startOf('week');
      loadSchedule();
    };

    const getEventsForHour = (date, hour) => {
      const formattedDate = moment(date).format('YYYY-MM-DD');

      return appointments.value.filter(app => {
        // Filter by date and status if needed
        const appDate = moment(app.preferred_time).format('YYYY-MM-DD');
        const appHour = moment(app.preferred_time).hour();

        return (
          appDate === formattedDate &&
          appHour === hour &&
          (showCompleted.value || app.status !== 'completed')
        );
      });
    };

    const viewAppointmentDetails = (appointment) => {
      selectedAppointment.value = appointment;
      bsAppointmentDetailModal.show();
    };

    const completeAppointment = () => {
      if (!selectedAppointment.value || selectedAppointment.value.status !== 'assigned') return;

      bsAppointmentDetailModal.hide();
      completionRemarks.value = '';
      remarksError.value = '';
      bsCompleteAppointmentModal.show();
    };

    const submitCompletion = async () => {
      if (!selectedAppointment.value || isProcessing.value) return;

      // Validate remarks
      if (!completionRemarks.value.trim()) {
        remarksError.value = 'Please provide remarks about the completed service';
        return;
      }

      isProcessing.value = true;
      try {
        await store.dispatch('requests/completeRequest', {
          id: selectedAppointment.value.id,
          remarks: completionRemarks.value.trim()
        });

        window.showToast({
          type: 'success',
          title: 'Success',
          message: 'Service has been marked as completed!'
        });

        bsCompleteAppointmentModal.hide();
        loadSchedule(); // Refresh the schedule
      } catch (error) {
        window.showToast({
          type: 'error',
          title: 'Error',
          message: error.response?.data?.message || 'Failed to complete service. Please try again.'
        });
      } finally {
        isProcessing.value = false;
      }
    };

    // Formatting helpers
    const formatDayName = (date) => {
      return moment(date).format('ddd');
    };

    const formatDayDate = (date) => {
      return moment(date).format('MMM D');
    };

    const formatHourLabel = (hour) => {
      return moment().hour(hour).minute(0).format('h A');
    };

    const formatDateLong = (dateString) => {
      return moment(dateString).format('dddd, MMMM D, YYYY h:mm A');
    };

    const formatDateOnly = (dateString) => {
      return moment(dateString).format('MMM D, YYYY');
    };

    const formatDuration = (minutes) => {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;

      if (hours === 0) {
        return `${mins} minutes`;
      } else if (mins === 0) {
        return `${hours} hour${hours > 1 ? 's' : ''}`;
      } else {
        return `${hours} hour${hours > 1 ? 's' : ''} ${mins} min`;
      }
    };

    const formatTimeSlot = (startTime, duration) => {
      const start = moment(startTime);
      const end = moment(startTime).add(duration, 'minutes');
      return `${start.format('h:mm A')} - ${end.format('h:mm A')}`;
    };

    const formatAppointmentTime = (appointment) => {
      return moment(appointment.preferred_time).format('h:mm A');
    };

    const formatUpcomingDate = (dateString) => {
      const date = moment(dateString);
      // eslint-disable-next-line no-unused-vars
      const today = moment().startOf('day');
      const tomorrow = moment().add(1, 'day').startOf('day');

      if (date.isSame(tomorrow, 'day')) {
        return `Tomorrow at ${date.format('h:mm A')}`;
      } else {
        return date.format('ddd, MMM D [at] h:mm A');
      }
    };

    const formatPhone = (phone) => {
      return `+91 ${phone}`;
    };

    const formatStatus = (status) => {
      const statusMap = {
        'created': 'Pending',
        'assigned': 'In Progress',
        'completed': 'Completed'
      };
      return statusMap[status] || status;
    };

    const isToday = (date) => {
      return moment(date).isSame(moment(), 'day');
    };

    const getAppointmentClass = (appointment) => {
      return {
        'assigned': appointment.status === 'assigned',
        'completed': appointment.status === 'completed',
        'created': appointment.status === 'created'
      };
    };

    const getAppointmentStyle = (appointment) => {
      // Calculate height based on duration (30 minutes = 50px height)
      const durationInMinutes = appointment.service.estimated_time;
      const heightPerMinute = 50 / 60; // 50px per hour
      const height = Math.max(durationInMinutes * heightPerMinute, 25); // Min height: 25px

      return {
        height: `${height}px`
      };
    };

    const getStatusBadgeClass = (status) => {
      const classMap = {
        'created': 'bg-warning',
        'assigned': 'bg-info',
        'completed': 'bg-success'
      };
      return classMap[status] || 'bg-secondary';
    };

    // Watch for changes in showCompleted and reload if necessary
    watch(showCompleted, () => {
      // No need to reload data, just recompute filtered lists
    });

    // Lifecycle hooks
    onMounted(() => {
      if (appointmentDetailModal.value) {
        bsAppointmentDetailModal = new bootstrap.Modal(appointmentDetailModal.value);
      }

      if (completeAppointmentModal.value) {
        bsCompleteAppointmentModal = new bootstrap.Modal(completeAppointmentModal.value);
      }

      loadSchedule();
    });

    return {
      isLoading,
      error,
      showCompleted,
      appointments,
      weekDays,
      displayHours,
      currentWeekStart,
      todayAppointments,
      upcomingAppointments,
      selectedAppointment,
      completionRemarks,
      remarksError,
      isProcessing,
      appointmentDetailModal,
      completeAppointmentModal,

      // Methods
      loadSchedule,
      refreshSchedule,
      prevWeek,
      nextWeek,
      todayWeek,
      getEventsForHour,
      viewAppointmentDetails,
      completeAppointment,
      submitCompletion,

      // Formatting helpers
      formatDayName,
      formatDayDate,
      formatHourLabel,
      formatDateLong,
      formatDateOnly,
      formatDuration,
      formatTimeSlot,
      formatAppointmentTime,
      formatUpcomingDate,
      formatPhone,
      formatStatus,
      isToday,
      getAppointmentClass,
      getAppointmentStyle,
      getStatusBadgeClass
    };
  }
};
</script>

<style scoped>
.table {
  table-layout: fixed;
}

.time-column {
  width: 80px;
  text-align: right;
  font-weight: 500;
  color: #6c757d;
  padding-right: 15px;
}

.hour-label {
  position: relative;
  top: -10px;
}

.day-header {
  padding: 10px 0;
}

.day-name {
  font-weight: 500;
}

.day-date {
  font-size: 0.875rem;
  color: #6c757d;
}

.schedule-cell {
  height: 50px;
  padding: 0;
  position: relative;
  vertical-align: top;
}

.today {
  background-color: rgba(var(--bs-primary-rgb), 0.05);
}

.appointment-card {
  position: absolute;
  width: 95%;
  margin: 2%;
  border-radius: 4px;
  padding: 5px 8px;
  font-size: 0.8rem;
  overflow: hidden;
  z-index: 1;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.appointment-card:hover {
  transform: scale(1.02);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
  z-index: 2;
}

.appointment-card.assigned {
  background-color: rgba(var(--bs-info-rgb), 0.15);
  border-left: 3px solid var(--bs-info);
}

.appointment-card.completed {
  background-color: rgba(var(--bs-success-rgb), 0.15);
  border-left: 3px solid var(--bs-success);
}

.appointment-card.created {
  background-color: rgba(var(--bs-warning-rgb), 0.15);
  border-left: 3px solid var(--bs-warning);
}

.appointment-time {
  font-weight: 500;
  font-size: 0.7rem;
}

.appointment-title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.appointment-customer {
  font-size: 0.7rem;
  color: #6c757d;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

/* Responsive styles */
@media (max-width: 767.98px) {
  .time-column {
    width: 60px;
    padding-right: 10px;
  }

  .day-header {
    padding: 5px 0;
  }

  .appointment-card {
    padding: 3px 5px;
  }
}
</style>
