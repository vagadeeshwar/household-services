# src/schemas/admin.py

from marshmallow import fields, Schema
from .base import BaseSchema


class ProfessionalsListQuerySchema(Schema):
    """Schema for validating professional list query parameters"""

    verified = fields.Bool(required=False)
    service_type = fields.Int(required=False)
    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)


class CustomersListQuerySchema(Schema):
    """Schema for validating customer list query parameters"""

    active = fields.Bool(required=False)
    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)


class BlockUserSchema(BaseSchema):
    """Schema for blocking user requests"""

    reason = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)


class ReviewActionSchema(BaseSchema):
    """Schema for handling review actions"""

    action = fields.Str(required=True, validate=lambda x: x in ["dismiss", "remove"])


class DashboardStatsSchema(Schema):
    """Schema for dashboard statistics output"""

    total_professionals = fields.Int(required=True)
    verified_professionals = fields.Int(required=True)
    total_customers = fields.Int(required=True)
    active_customers = fields.Int(required=True)
    pending_verifications = fields.Int(required=True)
    reported_reviews = fields.Int(required=True)
    service_requests = fields.Dict(
        keys=fields.Str(), values=fields.Int(), required=True
    )
