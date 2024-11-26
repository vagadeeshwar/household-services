from marshmallow import fields, Schema

from src.schemas.base import (
    BaseUserSchema,
    BaseProfileUpdateSchema,
    BaseUserInputSchema,
)


class CustomerRegisterSchema(BaseUserInputSchema):
    pass


class CustomerUpdateSchema(BaseProfileUpdateSchema):
    """Schema for customer profile updates"""

    pass


class CustomerOutputSchema(BaseUserSchema):
    """Customer output schema - includes all user fields"""

    pass


class CustomerQuerySchema(Schema):
    """Schema for validating customer list query parameters"""

    active = fields.Bool(required=False)
    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)


customer_output_schema = CustomerOutputSchema()
customer_update_schema = CustomerUpdateSchema()
customer_query_schema = CustomerQuerySchema()
customer_register_schema = CustomerRegisterSchema()
