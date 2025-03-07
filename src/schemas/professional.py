from marshmallow import Schema, fields, validate

from src.schemas.base import (
    BaseProfileUpdateSchema,
    BaseUserInputSchema,
    BaseUserSchema,
)


class ProfessionalRegisterSchema(BaseUserInputSchema):
    service_type_id = fields.Int(required=True)
    experience_years = fields.Int(required=True, validate=validate.Range(min=0, max=50))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=1000))


class ProfessionalUpdateSchema(BaseProfileUpdateSchema):
    """Schema for professional profile updates"""

    description = fields.Str(validate=validate.Length(min=10, max=1000))


class ProfessionalOutputSchema(BaseUserSchema):
    """Professional output schema - includes all user fields plus professional-specific fields"""

    professional_id = fields.Int(attribute="professional_profile.id", dump_only=True)
    service_type_id = fields.Int(attribute="professional_profile.service_type_id")
    experience_years = fields.Int(attribute="professional_profile.experience_years")
    description = fields.Str(attribute="professional_profile.description")
    is_verified = fields.Bool(
        attribute="professional_profile.is_verified", dump_only=True
    )
    average_rating = fields.Float(
        attribute="professional_profile.average_rating", dump_only=True
    )
    verification_documents = fields.Str(
        attribute="professional_profile.verification_documents", dump_only=True
    )


class ProfessionalQuerySchema(Schema):
    """Schema for validating professional list query parameters"""

    verified = fields.Bool(required=False)
    service_type = fields.Int(required=False)
    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)


professional_output_schema = ProfessionalOutputSchema()
professionals_output_schema = ProfessionalOutputSchema(many=True)
professional_update_schema = ProfessionalUpdateSchema()
professional_query_schema = ProfessionalQuerySchema()
professional_register_schema = ProfessionalRegisterSchema()
