from marshmallow import fields, Schema, validate

from src.schemas.base import (
    BaseUserSchema,
    BaseProfileUpdateSchema,
    BaseUserInputSchema,
)


class ProfessionalRegisterInputSchema(BaseUserInputSchema):
    service_type_id = fields.Int(required=True)
    experience_years = fields.Int(required=True, validate=validate.Range(min=0, max=50))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=1000))


class ProfessionalProfileUpdateSchema(BaseProfileUpdateSchema):
    """Schema for professional profile updates"""

    description = fields.Str(validate=validate.Length(min=10, max=1000))


class ProfessionalOutputSchema(BaseUserSchema):
    """Professional output schema - includes all user fields plus professional-specific fields"""

    service_type_id = fields.Int(required=True)
    experience_years = fields.Int(required=True)
    description = fields.Str(required=True)
    is_verified = fields.Bool(dump_only=True)
    average_rating = fields.Float(dump_only=True)
    verification_documents = fields.Str(dump_only=True)


class ProfessionalsListQuerySchema(Schema):
    """Schema for validating professional list query parameters"""

    verified = fields.Bool(required=False)
    service_type = fields.Int(required=False)
    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)


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


professional_output_schema = ProfessionalOutputSchema()
professional_profile_update_schema = ProfessionalProfileUpdateSchema()
professionals_list_query_schema = ProfessionalsListQuerySchema()
professional_register_schema = ProfessionalRegisterInputSchema()
