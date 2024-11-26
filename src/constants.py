USER_ROLE_ADMIN = "admin"
USER_ROLE_PROFESSIONAL = "professional"
USER_ROLE_CUSTOMER = "customer"
USER_ROLES = [USER_ROLE_ADMIN, USER_ROLE_PROFESSIONAL, USER_ROLE_CUSTOMER]

REQUEST_STATUS_CREATED = "created"
REQUEST_STATUS_ASSIGNED = "assigned"
REQUEST_STATUS_IN_PROGRESS = "in_progress"
REQUEST_STATUS_COMPLETED = "completed"
REQUEST_STATUSES = [
    REQUEST_STATUS_CREATED,
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_COMPLETED,
    REQUEST_STATUS_IN_PROGRESS,
]

# User Management Actions
USER_LOGIN = "user_login"
USER_REGISTER = "user_register"
USER_PROFILE_UPDATE = "profile_update"
USER_PASSWORD_CHANGE = "password_change"
USER_DELETE = "user_delete"

# Professional Management Actions
PROFESSIONAL_VERIFY = "professional_verify"
PROFESSIONAL_BLOCK = "professional_block"
PROFESSIONAL_UNBLOCK = "professional_unblock"
PROFESSIONAL_DOCUMENT_UPDATE = "document_update"
PROFESSIONAL_SERVICE_UPDATE = "service_update"

# Customer Management Actions
CUSTOMER_BLOCK = "customer_block"
CUSTOMER_UNBLOCK = "customer_unblock"

# Service Management Actions
SERVICE_CREATE = "service_create"
SERVICE_UPDATE = "service_update"
SERVICE_DELETE = "service_delete"
SERVICE_RESTORE = "service_restore"

# Request Management Actions
REQUEST_CREATE = "request_create"
REQUEST_ASSIGN = "request_assign"
REQUEST_START = "request_start"
REQUEST_COMPLETE = "request_complete"
REQUEST_REVIEWED = "request_reviewed"
REQUEST_CANCEL = "request_cancel"

# Review Management Actions
REVIEW_SUBMIT = "review_submit"
REVIEW_REPORT = "review_report"
REVIEW_DISMISS = "review_dismiss"
REVIEW_REMOVE = "review_remove"

# Payment Related Actions (if needed in future)
# PAYMENT_INITIATE = "payment_initiate"
# PAYMENT_SUCCESS = "payment_success"
# PAYMENT_FAIL = "payment_fail"
# PAYMENT_REFUND = "payment_refund"

# Admin Actions
# ADMIN_SETTINGS_UPDATE = "settings_update"
# ADMIN_BULK_ACTION = "bulk_action"

# System Actions
# SYSTEM_MAINTENANCE = "system_maintenance"
# SYSTEM_ERROR = "system_error"


# Group these constants in a class for better organization
class ActivityLogActions:
    """Constants for activity log actions"""

    # User Management
    USER_LOGIN = USER_LOGIN
    USER_REGISTER = USER_REGISTER
    USER_PROFILE_UPDATE = USER_PROFILE_UPDATE
    USER_PASSWORD_CHANGE = USER_PASSWORD_CHANGE
    USER_DELETE = USER_DELETE

    # Professional Management
    PROFESSIONAL_VERIFY = PROFESSIONAL_VERIFY
    PROFESSIONAL_BLOCK = PROFESSIONAL_BLOCK
    PROFESSIONAL_UNBLOCK = PROFESSIONAL_UNBLOCK
    PROFESSIONAL_DOCUMENT_UPDATE = PROFESSIONAL_DOCUMENT_UPDATE
    PROFESSIONAL_SERVICE_UPDATE = PROFESSIONAL_SERVICE_UPDATE

    # Customer Management
    CUSTOMER_BLOCK = CUSTOMER_BLOCK
    CUSTOMER_UNBLOCK = CUSTOMER_UNBLOCK

    # Service Management
    SERVICE_CREATE = SERVICE_CREATE
    SERVICE_UPDATE = SERVICE_UPDATE
    SERVICE_DELETE = SERVICE_DELETE
    SERVICE_RESTORE = SERVICE_RESTORE

    # Request Management
    REQUEST_CREATE = REQUEST_CREATE
    REQUEST_ASSIGN = REQUEST_ASSIGN
    REQUEST_START = REQUEST_START
    REQUEST_COMPLETE = REQUEST_COMPLETE
    REQUEST_CANCEL = REQUEST_CANCEL

    # Review Management
    REVIEW_SUBMIT = REVIEW_SUBMIT
    REVIEW_REPORT = REVIEW_REPORT
    REVIEW_DISMISS = REVIEW_DISMISS
    REVIEW_REMOVE = REVIEW_REMOVE

    # Payment Related
    # PAYMENT_INITIATE = PAYMENT_INITIATE
    # PAYMENT_SUCCESS = PAYMENT_SUCCESS
    # PAYMENT_FAIL = PAYMENT_FAIL
    # PAYMENT_REFUND = PAYMENT_REFUND

    # # Admin Actions
    # ADMIN_SETTINGS_UPDATE = ADMIN_SETTINGS_UPDATE
    # ADMIN_BULK_ACTION = ADMIN_BULK_ACTION

    # # System Actions
    # SYSTEM_MAINTENANCE = SYSTEM_MAINTENANCE
    # SYSTEM_ERROR = SYSTEM_ERROR

    @classmethod
    def get_all_actions(cls):
        """Returns list of all valid activity log actions"""
        return [
            getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith("_") and isinstance(getattr(cls, attr), str)
        ]
