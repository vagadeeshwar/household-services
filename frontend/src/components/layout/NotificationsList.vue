<!-- src/components/layout/NotificationsList.vue -->
<template>
    <div class="notifications-list">
        <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="notifications.length === 0" class="text-center py-4">
            <i class="bi bi-bell-slash fs-1 text-muted"></i>
            <p class="mt-2 text-muted mb-0">No notifications yet</p>
        </div>

        <div v-else class="list-group list-group-flush">
            <a v-for="notification in notifications" :key="notification.id" href="#"
                class="list-group-item list-group-item-action" :class="{ 'unread': !notification.read }"
                @click.prevent="handleNotificationClick(notification)">
                <div class="d-flex align-items-center">
                    <div :class="['notification-icon', notification.type]">
                        <i :class="getNotificationIcon(notification.type)"></i>
                    </div>
                    <div class="ms-3 flex-grow-1">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <strong class="notification-title">{{ notification.title }}</strong>
                            <small class="text-muted">{{ formatTime(notification.created_at) }}</small>
                        </div>
                        <p class="notification-message mb-0">{{ notification.message }}</p>
                    </div>
                </div>
            </a>
        </div>

        <div v-if="hasMore" class="text-center py-3">
            <button class="btn btn-link btn-sm" @click="loadMore" :disabled="loadingMore">
                <span v-if="loadingMore" class="spinner-border spinner-border-sm me-1"></span>
                Load More
            </button>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import moment from 'moment';

export default {
    name: 'NotificationsList',

    setup() {
        const router = useRouter();
        const notifications = ref([]);
        const loading = ref(true);
        const loadingMore = ref(false);
        const hasMore = ref(false);
        const page = ref(1);

        const getNotificationIcon = (type) => {
            const icons = {
                'request': 'bi-clipboard-check',
                'review': 'bi-star',
                'service': 'bi-tools',
                'account': 'bi-person',
                'system': 'bi-gear',
                'default': 'bi-bell'
            };
            return icons[type] || icons.default;
        };

        const loadNotifications = async (isLoadMore = false) => {
            if (isLoadMore) {
                loadingMore.value = true;
            } else {
                loading.value = true;
            }

            try {
                const response = await fetch(`/api/notifications?page=${page.value}`);
                const data = await response.json();

                if (isLoadMore) {
                    notifications.value.push(...data.items);
                } else {
                    notifications.value = data.items;
                }

                hasMore.value = data.has_more;
                page.value++;
            } catch (error) {
                console.error('Error loading notifications:', error);
            } finally {
                loading.value = false;
                loadingMore.value = false;
            }
        };

        const handleNotificationClick = async (notification) => {
            try {
                if (!notification.read) {
                    await fetch(`/api/notifications/${notification.id}/read`, {
                        method: 'POST'
                    });
                }

                // Navigate based on notification type
                if (notification.link) {
                    router.push(notification.link);
                }
            } catch (error) {
                console.error('Error marking notification as read:', error);
            }
        };

        const formatTime = (date) => {
            return moment(date).fromNow();
        };

        const loadMore = () => {
            loadNotifications(true);
        };

        // Load initial notifications
        loadNotifications();

        return {
            notifications,
            loading,
            loadingMore,
            hasMore,
            getNotificationIcon,
            handleNotificationClick,
            formatTime,
            loadMore
        };
    }
};
</script>

<style scoped>
.notifications-list {
    max-height: calc(100vh - 150px);
    overflow-y: auto;
}

.notification-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.notification-icon.request {
    background-color: rgba(13, 110, 253, 0.1);
    color: #0d6efd;
}

.notification-icon.review {
    background-color: rgba(255, 193, 7, 0.1);
    color: #ffc107;
}

.notification-icon.service {
    background-color: rgba(25, 135, 84, 0.1);
    color: #198754;
}

.notification-icon.account {
    background-color: rgba(13, 202, 240, 0.1);
    color: #0dcaf0;
}

.notification-icon.system {
    background-color: rgba(108, 117, 125, 0.1);
    color: #6c757d;
}

.list-group-item.unread {
    background-color: rgba(13, 110, 253, 0.05);
}

.list-group-item:hover {
    background-color: rgba(0, 0, 0, 0.02);
}

.notification-title {
    font-size: 0.9375rem;
}

.notification-message {
    font-size: 0.875rem;
    color: #6c757d;
}

.btn-link {
    text-decoration: none;
}

.btn-link:hover {
    text-decoration: underline;
}
</style>