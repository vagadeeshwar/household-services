# src/schemas/user.py

from marshmallow import fields, Schema, validate, validates
from .base import BaseSchema


class BaseUserSchema(Schema):
    """Base schema for user data"""

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    full_name = fields.Str(required=True)
    phone = fields.Str(required=True)
    address = fields.Str(required=True)
    pin_code = fields.Str(required=True)
    role = fields.Str(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)


class CustomerOutputSchema(BaseUserSchema):
    """Customer output schema - includes all user fields"""


class ProfessionalOutputSchema(BaseUserSchema):
    """Professional output schema - includes all user fields plus professional-specific fields"""

    service_type_id = fields.Int(required=True)
    experience_years = fields.Int(required=True)
    description = fields.Str(required=True)
    is_verified = fields.Bool(dump_only=True)
    average_rating = fields.Float(dump_only=True)
    verification_documents = fields.Str(dump_only=True)


class BaseProfileUpdateSchema(BaseSchema):
    """Base schema for profile updates"""

    email = fields.Email()
    full_name = fields.Str(validate=validate.Length(min=4, max=100))
    phone = fields.Str()
    address = fields.Str(validate=validate.Length(min=5, max=200))
    pin_code = fields.Str()

    @validates("phone")
    def validate_phone_field(self, value):
        self.validate_phone(value)

    @validates("pin_code")
    def validate_pincode_field(self, value):
        self.validate_pincode(value)


class CustomerProfileUpdateSchema(BaseProfileUpdateSchema):
    """Schema for customer profile updates"""

    pass


class ProfessionalProfileUpdateSchema(BaseProfileUpdateSchema):
    """Schema for professional profile updates"""

    description = fields.Str(validate=validate.Length(min=10, max=1000))


# Method to combine user and professional profile data
def combine_professional_data(user, profile):
    """Combine user and professional profile data into a single dict"""
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "address": user.address,
        "pin_code": user.pin_code,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "service_type_id": profile.service_type_id,
        "experience_years": profile.experience_years,
        "description": profile.description,
        "is_verified": profile.is_verified,
        "average_rating": profile.average_rating,
        "verification_documents": profile.verification_documents,
    }
    return data
