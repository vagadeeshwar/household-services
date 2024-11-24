from marshmallow import Schema, ValidationError
import re


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
