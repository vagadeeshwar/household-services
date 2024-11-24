from marshmallow import Schema, fields, validate, validates, ValidationError
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


# Input Schemas
class LoginInput(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class BaseUserInput(BaseSchema):
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(
                min=4, max=20, error="Username must be between 4 and 20 characters"
            ),
            validate.Regexp(
                r"^[a-zA-Z0-9_.-]+$",
                error="Username can only contain letters, numbers, and _ . -",
            ),
        ],
    )
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    full_name = fields.Str(
        required=True,
        validate=[
            validate.Length(
                min=4, max=20, error="Full name must be between 4 and 20 characters"
            ),
            validate.Regexp(
                r"^[a-zA-Z\s.-]+$",
                error="Full name can only contain letters, spaces, dots, and hyphens",
            ),
        ],
    )
    phone = fields.Str(required=True)
    address = fields.Str(
        required=True,
        validate=validate.Length(
            min=5, max=200, error="Address must be between 5 and 200 characters"
        ),
    )
    pin_code = fields.Str(required=True)

    @validates("phone")
    def validate_phone_field(self, value: str) -> None:
        self.validate_phone(value)

    @validates("password")
    def validate_password_field(self, value: str) -> None:
        self.validate_password(value)

    @validates("pin_code")
    def validate_pincode_field(self, value: str) -> None:
        self.validate_pincode(value)


class CustomerRegisterInput(BaseUserInput):
    pass


class ProfessionalRegisterInput(BaseUserInput):
    service_type_id = fields.Int(required=True)
    experience_years = fields.Int(required=True, validate=validate.Range(min=0, max=50))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=1000))
    verification_documents = fields.Str(
        validate=validate.Regexp(
            r"^[\w\-. ]+\.(pdf|jpg|jpeg|png)$",
            error="Invalid document format. Allowed: pdf, jpg, jpeg, png",
        )
    )


class PasswordUpdateInput(BaseSchema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True)

    @validates("new_password")
    def validate_new_password(self, value: str) -> None:
        self.validate_password(value)


# Output Schemas
class TokenOutput(Schema):
    token = fields.Str(required=True)


class ErrorOutput(Schema):
    status = fields.Str(required=True)
    status_code = fields.Int(required=True)
    detail = fields.Str(required=True)
    error_type = fields.Str(required=True)


class BaseUserOutput(Schema):
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


class CustomerOutput(BaseUserOutput):
    pass


class ProfessionalOutput(BaseUserOutput):
    service_type_id = fields.Int(required=True)
    experience_years = fields.Int(required=True)
    description = fields.Str(required=True)
    is_verified = fields.Bool(required=True)
    average_rating = fields.Float(required=True)
    verification_documents = fields.Str(allow_none=True)


class ServiceOutput(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    base_price = fields.Float(required=True)
    time_required = fields.Int(required=True)
    is_active = fields.Bool(required=True)


class ReviewOutput(Schema):
    id = fields.Int(required=True)
    rating = fields.Int(required=True)
    comment = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)
    service_request_id = fields.Int(required=True)


class ServiceRequestOutput(Schema):
    id = fields.Int(required=True)
    service = fields.Nested(ServiceOutput)
    customer = fields.Nested(CustomerOutput)
    professional = fields.Nested(ProfessionalOutput, allow_none=True)
    date_of_request = fields.DateTime(required=True)
    preferred_time = fields.Str(allow_none=True)
    status = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    date_of_assignment = fields.DateTime(allow_none=True)
    date_of_completion = fields.DateTime(allow_none=True)
    remarks = fields.Str(allow_none=True)
    review = fields.Nested(ReviewOutput, allow_none=True)


# Initialize schemas
login_input_schema = LoginInput()
customer_register_input_schema = CustomerRegisterInput()
professional_register_input_schema = ProfessionalRegisterInput()
password_update_input_schema = PasswordUpdateInput()

token_output_schema = TokenOutput()
error_output_schema = ErrorOutput()
customer_output_schema = CustomerOutput()
professional_output_schema = ProfessionalOutput()
service_output_schema = ServiceOutput()
review_output_schema = ReviewOutput()
service_request_output_schema = ServiceRequestOutput()

# List schemas
customers_output_schema = CustomerOutput(many=True)
professionals_output_schema = ProfessionalOutput(many=True)
services_output_schema = ServiceOutput(many=True)
reviews_output_schema = ReviewOutput(many=True)
service_requests_output_schema = ServiceRequestOutput(many=True)
