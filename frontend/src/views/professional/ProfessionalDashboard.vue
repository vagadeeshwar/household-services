# src/views/professional/ProfessionalDashboard.vue
<template>
    <div class="container-fluid py-4">
        <!-- Stats Cards Row -->
        <div class="row g-4 mb-4">
            <!-- Earnings Card -->
            <div class="col-md-6 col-lg-3">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-primary bg-opacity-10 p-3 rounded-circle">
                                <i class="bi bi-currency-rupee fs-4 text-primary"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Total Earnings</h6>
                                <h3 class="mb-0">₹{{ stats.earnings?.total || 0 }}</h3>
                            </div>
                        </div>
                        <div class="progress" style="height: 4px;">
                            <div class="progress-bar" :style="{ width: earningsProgress + '%' }" role="progressbar">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Requests Card -->
            <div class="col-md-6 col-lg-3">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-success bg-opacity-10 p-3 rounded-circle">
                                <i class="bi bi-list-check fs-4 text-success"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Active Requests</h6>
                                <h3 class="mb-0">{{ stats.requests?.active || 0 }}</h3>
                            </div>
                        </div>
                        <div class="progress" style="height: 4px;">
                            <div class="progress-bar bg-success" :style="{ width: requestProgress + '%' }"
                                role="progressbar"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Rating Card -->
            <div class="col-md-6 col-lg-3">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-warning bg-opacity-10 p-3 rounded-circle">
                                <i class="bi bi-star fs-4 text-warning"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Average Rating</h6>
                                <h3 class="mb-0">{{ stats.rating?.average || 0 }}/5</h3>
                            </div>
                        </div>
                        <div class="d-flex align-items-center">
                            <div class="rating text-warning me-2">
                                <i v-for="n in 5" :key="n" class="bi"
                                    :class="n <= (stats.rating?.average || 0) ? 'bi-star-fill' : 'bi-star'"></i>
                            </div>
                            <small class="text-muted">({{ stats.rating?.total || 0 }} reviews)</small>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Completion Rate Card -->
            <div class="col-md-6 col-lg-3">
                <div class="card border-0 shadow-sm h-100">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="bg-info bg-opacity-10 p-3 rounded-circle">
                                <i class="bi bi-check-circle fs-4 text-info"></i>
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">Completion Rate</h6>
                                <h3 class="mb-0">{{ completionRate }}%</h3>
                            </div>
                        </div>
                        <div class="progress" style="height: 4px;">
                            <div class="progress-bar bg-info" :style="{ width: completionRate + '%' }"
                                role="progressbar"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="row g-4 mb-4">
            <!-- Earnings Chart -->
            <div class="col-lg-8">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent">
                        <h5 class="mb-0">Earnings Overview</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="earningsChart" ref="earningsChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Request Distribution -->
            <div class="col-lg-4">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent">
                        <h5 class="mb-0">Request Distribution</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="requestsChart" ref="requestsChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Activities Row -->
        <div class="row g-4">
            <!-- Today's Schedule -->
            <div class="col-lg-6">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Today's Schedule</h5>
                        <button class="btn btn-sm btn-outline-primary">View All</button>
                    </div>
                    <div class="card-body p-0">
                        <div v-if="!todaySchedule.length" class="text-center py-4">
                            <i class="bi bi-calendar2-check fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No appointments scheduled for today</p>
                        </div>
                        <div v-else class="list-group list-group-flush">
                            <div v-for="appointment in todaySchedule" :key="appointment.id" class="list-group-item">
                                <div class="d-flex align-items-center">
                                    <div class="bg-light rounded-circle p-3 me-3">
                                        <i class="bi bi-clock text-primary"></i>
                                    </div>
                                    <div class="flex-grow-1">
                                        <h6 class="mb-0">{{ appointment.customer_name }}</h6>
                                        <p class="text-muted mb-0 small">
                                            {{ formatTime(appointment.scheduled_time) }} - {{ appointment.service }}
                                        </p>
                                    </div>
                                    <button class="btn btn-sm btn-outline-primary">Details</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Reviews -->
            <div class="col-lg-6">
                <div class="card border-0 shadow-sm">
                    <div class="card-header bg-transparent d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Recent Reviews</h5>
                        <button class="btn btn-sm btn-outline-primary">View All</button>
                    </div>
                    <div class="card-body p-0">
                        <div v-if="!recentReviews.length" class="text-center py-4">
                            <i class="bi bi-star fs-1 text-muted"></i>
                            <p class="mt-2 mb-0">No reviews yet</p>
                        </div>
                        <div v-else class="list-group list-group-flush">
                            <div v-for="review in recentReviews" :key="review.id" class="list-group-item">
                                <div class="d-flex align-items-start">
                                    <div class="flex-grow-1">
                                        <div class="d-flex align-items-center mb-1">
                                            <div class="rating text-warning me-2">
                                                <i v-for="n in 5" :key="n" class="bi"
                                                    :class="n <= review.rating ? 'bi-star-fill' : 'bi-star'"></i>
                                            </div>
                                            <small class="text-muted">{{ formatDate(review.created_at) }}</small>
                                        </div>
                                        <p class="mb-1">{{ review.comment }}</p>
                                        <small class="text-muted">{{ review.customer_name }}</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import Chart from 'chart.js/auto';
import moment from 'moment';

export default {
    name: 'ProfessionalDashboard',

    setup() {
        const earningsChart = ref(null);
        const requestsChart = ref(null);
        const stats = ref({
            earnings: {
                total: 15000,
                monthly: [12000, 13500, 15000, 14000, 15000, 16000],
                target: 20000
            },
            requests: {
                active: 5,
                completed: 45,
                cancelled: 2,
                total: 52
            },
            rating: {
                average: 4.5,
                total: 40
            }
        });

        const todaySchedule = ref([
            {
                id: 1,
                customer_name: 'John Doe',
                service: 'AC Repair',
                scheduled_time: '2024-03-29T10:00:00'
            },
            {
                id: 2,
                customer_name: 'Jane Smith',
                service: 'AC Maintenance',
                scheduled_time: '2024-03-29T14:00:00'
            }
        ]);

        const recentReviews = ref([
            {
                id: 1,
                customer_name: 'Mike Johnson',
                rating: 5,
                comment: 'Excellent service! Very professional and on time.',
                created_at: '2024-03-28T15:30:00'
            },
            {
                id: 2,
                customer_name: 'Sarah Wilson',
                rating: 4,
                comment: 'Good service, would recommend.',
                created_at: '2024-03-27T11:20:00'
            }
        ]);

        // Computed Properties
        const completionRate = computed(() => {
            const { completed, total } = stats.value.requests;
            return total ? Math.round((completed / total) * 100) : 0;
        });

        const earningsProgress = computed(() => {
            const { total, target } = stats.value.earnings;
            return Math.min(Math.round((total / target) * 100), 100);
        });

        const requestProgress = computed(() => {
            const { active, total } = stats.value.requests;
            return total ? Math.round((active / total) * 100) : 0;
        });

        // Methods
        const initCharts = () => {
            // Earnings Chart
            if (earningsChart.value) {
                new Chart(earningsChart.value, {
                    type: 'line',
                    data: {
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        datasets: [{
                            label: 'Monthly Earnings',
                            data: stats.value.earnings.monthly,
                            borderColor: '#0d6efd',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                            }
                        }
                    }
                });
            }

            // Requests Chart
            if (requestsChart.value) {
                new Chart(requestsChart.value, {
                    type: 'doughnut',
                    data: {
                        labels: ['Active', 'Completed', 'Cancelled'],
                        datasets: [{
                            data: [
                                stats.value.requests.active,
                                stats.value.requests.completed,
                                stats.value.requests.cancelled
                            ],
                            backgroundColor: ['#0d6efd', '#198754', '#dc3545']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        };

        const formatTime = (time) => {
            return moment(time).format('h:mm A');
        };

        const formatDate = (date) => {
            return moment(date).fromNow();
        };

        // Lifecycle Hooks
        onMounted(() => {
            initCharts();
        });

        return {
            stats,
            todaySchedule,
            recentReviews,
            earningsChart,
            requestsChart,
            completionRate,
            earningsProgress,
            requestProgress,
            formatTime,
            formatDate
        };
    }
};
</script>

<style scoped>
.rating i {
    font-size: 0.875rem;
}

.card {
    transition: transform 0.2s ease-in-out;
}

.card:hover {
    transform: translateY(-2px);
}

.progress {
    border-radius: 2px;
}

.progress-bar {
    transition: width 1s ease-in-out;
}

.list-group-item {
    transition: background-color 0.2s ease-in-out;
}

.list-group-item:hover {
    background-color: #f8f9fa;
}
</style>