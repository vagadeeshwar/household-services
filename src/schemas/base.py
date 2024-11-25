import re
from marshmallow import fields, Schema, validate, validates, ValidationError


class BaseSchema(Schema):
    """Base schema with common validation methods"""

    @staticmethod
    def validate_phone(value: str) -> None:
        if not re.match(r"^[1-9]\d{9}$", value):
            raise ValidationError("Phone number must be 10 digits and not start with 0")

    @staticmethod
    def validate_password(value: str) -> None:
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", value):
            raise ValidationError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValidationError("Password must contain a lowercase letter")
        if not re.search(r"\d", value):
            raise ValidationError("Password must contain a number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Password must contain a special character")

    @staticmethod
    def validate_pincode(value: str) -> None:
        if not re.match(r"^[1-9][0-9]{5}$", value):
            raise ValidationError("PIN code must be 6 digits and not start with 0")


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
