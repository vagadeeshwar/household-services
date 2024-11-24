from marshmallow import fields, Schema, validate, validates
from .base import BaseSchema


class BaseUserOutputSchema(Schema):
    id = fields.Int(required=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    full_name = fields.Str(required=True)
    phone = fields.Str(required=True)
    address = fields.Str(required=True)
    pin_code = fields.Str(required=True)
    role = fields.Str(required=True)
    is_active = fields.Bool(required=True)
    created_at = fields.DateTime(required=True)
    last_login = fields.DateTime(allow_none=True)


class CustomerOutputSchema(BaseUserOutputSchema):
    pass


class ProfessionalOutputSchema(BaseUserOutputSchema):
    service_type_id = fields.Int(required=True)
    experience_years = fields.Int(required=True)
    description = fields.Str(required=True)
    is_verified = fields.Bool(required=True)
    average_rating = fields.Float(required=True)
    verification_documents = fields.Str(allow_none=True)


class BaseProfileUpdateSchema(BaseSchema):
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


class CustomerProfileUpdateInputSchema(BaseProfileUpdateSchema):
    pass


class ProfessionalProfileUpdateInputSchema(BaseProfileUpdateSchema):
    description = fields.Str(validate=validate.Length(min=10, max=1000))
