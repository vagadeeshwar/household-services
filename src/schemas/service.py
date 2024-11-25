from marshmallow import fields, validate, Schema
from .base import BaseSchema


class ServiceInputSchema(BaseSchema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=1000))
    base_price = fields.Float(required=True, validate=validate.Range(min=0))
    time_required = fields.Int(required=True, validate=validate.Range(min=1))
    is_active = fields.Bool()


class ServiceOutputSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    base_price = fields.Float(required=True)
    time_required = fields.Int(required=True)
    is_active = fields.Bool(required=True)

class ServiceListQuerySchema(Schema):
    """Schema for validating service list query parameters"""
    name = fields.Str(required=False)
    min_price = fields.Float(required=False)
    max_price = fields.Float(required=False)
    is_active = fields.Boolean(required=False)  # Only for admin
    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)

service_schema = ServiceOutputSchema()
services_schema = ServiceOutputSchema(many=True)
service_input_schema = ServiceInputSchema()
service_list_query_schema = ServiceListQuerySchema()
