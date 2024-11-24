from marshmallow import fields, validates, validate, Schema
from .base import BaseSchema


class LoginInputSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class BaseUserInputSchema(BaseSchema):
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=4, max=20),
            validate.Regexp(r"^[a-zA-Z0-9_.-]+$"),
        ],
    )
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    full_name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=4, max=100),
            validate.Regexp(r"^[a-zA-Z\s.-]+$"),
        ],
    )
    phone = fields.Str(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    pin_code = fields.Str(required=True)

    @validates("phone")
    def validate_phone_field(self, value):
        self.validate_phone(value)

    @validates("password")
    def validate_password_field(self, value):
        self.validate_password(value)

    @validates("pin_code")
    def validate_pincode_field(self, value):
        self.validate_pincode(value)


class CustomerRegisterInputSchema(BaseUserInputSchema):
    pass


class ProfessionalRegisterInputSchema(BaseUserInputSchema):
    service_type_id = fields.Int(required=True)
    experience_years = fields.Int(required=True, validate=validate.Range(min=0, max=50))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=1000))


class PasswordUpdateInputSchema(BaseSchema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True)

    @validates("new_password")
    def validate_new_password(self, value):
        self.validate_password(value)


class TokenOutputSchema(Schema):
    token = fields.Str(required=True)


class DeleteAccountInputSchema(BaseSchema):
    password = fields.Str(required=True)
