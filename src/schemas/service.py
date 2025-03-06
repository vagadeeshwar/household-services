from marshmallow import Schema, fields, validate

from src.schemas.base import BaseSchema


class ServiceInputSchema(BaseSchema):
    """Schema for creating/updating services"""

    name = fields.Str(required=True, validate=validate.Length(min=4, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    base_price = fields.Float(required=True, validate=validate.Range(min=0))
    estimated_time = fields.Int(required=True, validate=validate.Range(min=1))
    is_active = fields.Bool(dump_only=True)


class ServiceUpdateSchema(BaseSchema):
    """Schema for creating/updating services"""

    name = fields.Str(validate=validate.Length(min=4, max=100))
    description = fields.Str(validate=validate.Length(min=1, max=1000))
    base_price = fields.Float(validate=validate.Range(min=0))
    estimated_time = fields.Int(validate=validate.Range(min=1))


class ServiceOutputSchema(Schema):
    """Schema for service output data"""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    base_price = fields.Float(required=True)
    estimated_time = fields.Int(required=True)
    is_active = fields.Bool(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ServiceQuerySchema(Schema):
    """Schema for validating service list query parameters"""

    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)


# Initialize schemas
service_output_schema = ServiceOutputSchema()
services_output_schema = ServiceOutputSchema(many=True)
service_input_schema = ServiceInputSchema()
service_update_schema = ServiceUpdateSchema()
service_query_schema = ServiceQuerySchema()
