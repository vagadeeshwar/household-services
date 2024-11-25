from marshmallow import fields, Schema

from src.schemas.base import BaseUserSchema, BaseProfileUpdateSchema, BaseUserInputSchema

class CustomerRegisterInputSchema(BaseUserInputSchema):
    pass

class CustomerOutputSchema(BaseUserSchema):
    """Customer output schema - includes all user fields"""


class CustomerProfileUpdateSchema(BaseProfileUpdateSchema):
    """Schema for customer profile updates"""

    pass


class CustomersListQuerySchema(Schema):
    """Schema for validating customer list query parameters"""

    active = fields.Bool(required=False)
    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)


customer_output_schema = CustomerOutputSchema()
customer_profile_update_schema = CustomerProfileUpdateSchema()
customers_list_query_schema = CustomersListQuerySchema()
customer_register_schema = CustomerRegisterInputSchema()
