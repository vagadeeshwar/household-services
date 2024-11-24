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
