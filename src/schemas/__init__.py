from .auth import (
    LoginInputSchema,
    CustomerRegisterInputSchema,
    ProfessionalRegisterInputSchema,
    PasswordUpdateInputSchema,
    TokenOutputSchema,
    DeleteAccountInputSchema,
)
from .user import (
    CustomerOutputSchema,
    ProfessionalOutputSchema,
    CustomerProfileUpdateSchema,
    ProfessionalProfileUpdateSchema,
    combine_professional_data,  # noqa
)
from .service import (
    ServiceOutputSchema,
    ServiceInputSchema,
)
from .request import (
    ServiceRequestOutputSchema,
    ReviewOutputSchema,
)
from .admin import (
    ProfessionalsListQuerySchema,
    CustomersListQuerySchema,
    BlockUserSchema,
    ReviewActionSchema,
    DashboardStatsSchema,
)
from .error import ErrorOutputSchema

# Initialize schemas
# Auth schemas
login_schema = LoginInputSchema()
customer_register_schema = CustomerRegisterInputSchema()
professional_register_schema = ProfessionalRegisterInputSchema()
password_update_schema = PasswordUpdateInputSchema()
token_schema = TokenOutputSchema()
error_schema = ErrorOutputSchema()

# User schemas
customer_output_schema = CustomerOutputSchema()
professional_output_schema = ProfessionalOutputSchema()
customer_profile_update_schema = CustomerProfileUpdateSchema()
professional_profile_update_schema = ProfessionalProfileUpdateSchema()

# Service schemas
service_schema = ServiceOutputSchema()
services_schema = ServiceOutputSchema(many=True)
service_input_schema = ServiceInputSchema()

# Request and review schemas
service_request_schema = ServiceRequestOutputSchema()
service_requests_schema = ServiceRequestOutputSchema(many=True)
review_schema = ReviewOutputSchema()
reviews_schema = ReviewOutputSchema(many=True)

# Account management schemas
delete_account_schema = DeleteAccountInputSchema()

# Admin schemas
professionals_list_query_schema = ProfessionalsListQuerySchema()
customers_list_query_schema = CustomersListQuerySchema()
block_user_schema = BlockUserSchema()
review_action_schema = ReviewActionSchema()
dashboard_stats_schema = DashboardStatsSchema()
