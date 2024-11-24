from marshmallow import fields, validate, ValidationError
import re
from .models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    Service,
    ServiceRequest,
    Review,
    USER_ROLES,
    REQUEST_STATUSES,
)
from . import ma


def validate_phone(value):
    """Validate phone number format."""
    if not re.match(r"^[1-9]\d{9}$", value):
        raise ValidationError(
            "Invalid phone number. Must be 10-digit and can't start with a 0."
        )


def validate_password(value):
    """
    Validate password strength.
    Must contain:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", value):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", value):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", value):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError("Password must contain at least one special character.")


def validate_pincode(value):
    """Validate Indian PIN code format."""
    if not re.match(r"^[1-9][0-9]{5}$", value):
        raise ValidationError(
            "Invalid PIN code. Must be a 6-digit postal code not starting with 0."
        )


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = ma.auto_field(dump_only=True)

    username = ma.String(
        required=True,
        validate=[
            validate.Length(
                min=4, max=80, error="Username must be between 4 and 80 characters."
            ),
            validate.Regexp(
                r"^[a-zA-Z0-9_.-]+$",
                error="Username can only contain letters, numbers, and the characters _ . -",
            ),
        ],
    )
    email = ma.Email(
        required=True,
        validate=validate.Length(
            max=120, error="Email must not exceed 120 characters."
        ),
    )
    full_name = ma.String(
        validate=[
            validate.Length(
                min=4, max=100, error="Full name must be between 4 and 100 characters."
            ),
            validate.Regexp(
                r"^[a-zA-Z\s.-]+$",
                error="Full name can only contain letters, spaces, dots, and hyphens.",
            ),
        ],
    )

    phone = ma.String(required=True, validate=validate_phone)
    address = ma.String(
        required=True,
        validate=validate.Length(
            min=1, max=500, error="Address must be between 1 and 500 characters."
        ),
    )
    pin_code = ma.String(required=True, validate=validate_pincode)
    role = fields.String(required=True, validate=validate.OneOf(USER_ROLES))

    password = ma.String(load_only=True, validate=validate_password)
    is_active = ma.Boolean(dump_only=True)
    created_at = ma.DateTime(dump_only=True)
    updated_at = ma.DateTime(dump_only=True)
    last_login = ma.DateTime(dump_only=True)


class CustomerProfileSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CustomerProfile
        include_fk = True

    # Profile fields
    id = ma.auto_field(dump_only=True)
    created_at = ma.DateTime(dump_only=True)

    # User fields with all validations preserved
    username = fields.String(
        attribute="user.username",
        required=True,
        validate=[
            validate.Length(
                min=4, max=80, error="Username must be between 4 and 80 characters."
            ),
            validate.Regexp(
                r"^[a-zA-Z0-9_.-]+$",
                error="Username can only contain letters, numbers, and the characters _ . -",
            ),
        ],
    )
    email = fields.Email(
        attribute="user.email",
        required=True,
        validate=validate.Length(
            max=120, error="Email must not exceed 120 characters."
        ),
    )
    full_name = fields.String(
        attribute="user.full_name",
        validate=[
            validate.Length(
                min=4, max=100, error="Full name must be between 4 and 100 characters."
            ),
            validate.Regexp(
                r"^[a-zA-Z\s.-]+$",
                error="Full name can only contain letters, spaces, dots, and hyphens.",
            ),
        ],
    )
    phone = fields.String(
        attribute="user.phone", required=True, validate=validate_phone
    )
    address = fields.String(
        attribute="user.address",
        required=True,
        validate=validate.Length(
            min=1, max=500, error="Address must be between 1 and 500 characters."
        ),
    )
    pin_code = fields.String(
        attribute="user.pin_code", required=True, validate=validate_pincode
    )
    password = fields.String(load_only=True, required=True, validate=validate_password)
    role = fields.Function(lambda obj: obj.user.role)
    is_active = fields.Boolean(attribute="user.is_active", dump_only=True)


class ProfessionalProfileSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ProfessionalProfile
        include_fk = True

    # Profile specific fields with validations
    id = ma.auto_field(dump_only=True)
    experience_years = fields.Integer(
        required=True,
        validate=validate.Range(
            min=0, max=50, error="Experience must be between 0 and 50 years."
        ),
    )
    description = fields.String(
        validate=validate.Length(
            min=1,
            max=1000,
            error="Description must be between 1 and 1000 characters.",
        )
    )
    is_verified = fields.Boolean(dump_only=True)
    verification_documents = fields.String(
        validate=validate.Regexp(
            r"^[\w\-. ]+\.(pdf|jpg|jpeg|png)$",
            error="Invalid document format. Allowed formats: pdf, jpg, jpeg, png",
        )
    )
    service_type_id = fields.Integer(required=True)
    average_rating = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # User fields with all validations preserved
    username = fields.String(
        attribute="user.username",
        required=True,
        validate=[
            validate.Length(
                min=4, max=80, error="Username must be between 4 and 80 characters."
            ),
            validate.Regexp(
                r"^[a-zA-Z0-9_.-]+$",
                error="Username can only contain letters, numbers, and the characters _ . -",
            ),
        ],
    )
    email = fields.Email(
        attribute="user.email",
        required=True,
        validate=validate.Length(
            max=120, error="Email must not exceed 120 characters."
        ),
    )
    full_name = fields.String(
        attribute="user.full_name",
        validate=[
            validate.Length(
                min=4, max=100, error="Full name must be between 4 and 100 characters."
            ),
            validate.Regexp(
                r"^[a-zA-Z\s.-]+$",
                error="Full name can only contain letters, spaces, dots, and hyphens.",
            ),
        ],
    )
    phone = fields.String(
        attribute="user.phone", required=True, validate=validate_phone
    )
    address = fields.String(
        attribute="user.address",
        required=True,
        validate=validate.Length(
            min=1, max=500, error="Address must be between 1 and 500 characters."
        ),
    )
    pin_code = fields.String(
        attribute="user.pin_code", required=True, validate=validate_pincode
    )
    password = fields.String(load_only=True, required=True, validate=validate_password)
    role = fields.Function(lambda obj: obj.user.role)

    is_active = fields.Boolean(attribute="user.is_active", dump_only=True)

    # Include service relationship
    service_type = fields.Nested("ServiceSchema", only=("id", "name"), dump_only=True)


class ServiceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Service
        load_instance = True

    id = ma.auto_field(dump_only=True)

    name = ma.String(
        required=True,
        validate=[
            validate.Length(min=2, max=100),
            validate.Regexp(
                r"^[a-zA-Z0-9\s&-]+$",
                error="Service name can only contain letters, numbers, spaces, &, and hyphens.",
            ),
        ],
    )
    description = ma.String(
        validate=validate.Length(
            min=1,
            max=2000,
            error="Description must be between 1 and 2000 characters.",
        ),
    )
    base_price = ma.Float(
        required=True,
        validate=validate.Range(
            min=100, max=50000, error="Base price must be between ₹100 and ₹50,000."
        ),
    )

    time_required = ma.Integer(
        required=True,
        validate=validate.Range(
            min=15,
            max=480,  # 15 minutes to 8 hours
            error="Service duration must be between 15 and 480 minutes",
        ),
    )

    is_active = ma.Boolean()
    created_at = ma.DateTime(dump_only=True)

    professionals = fields.Nested(
        "ProfessionalProfileSchema",
        many=True,
        only=("id", "user.full_name", "average_rating"),
        dump_only=True,
    )


class ServiceRequestSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ServiceRequest
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    service_id = ma.Integer(required=True)
    customer_id = ma.Integer(required=True)
    professional_id = ma.Integer()
    date_of_request = ma.DateTime(required=True)
    preferred_time = ma.String()
    description = ma.String()
    status = fields.String(required=True, validate=validate.OneOf(REQUEST_STATUSES))
    date_of_assignment = ma.DateTime(dump_only=True)
    date_of_completion = ma.DateTime(dump_only=True)
    remarks = ma.String()
    created_at = ma.DateTime(dump_only=True)

    # Nested relationships
    service = fields.Nested(
        ServiceSchema, only=("id", "name", "base_price"), dump_only=True
    )
    customer = fields.Nested(
        CustomerProfileSchema,
        only=("id", "user.full_name", "user.phone"),
        dump_only=True,
    )
    professional = fields.Nested(
        ProfessionalProfileSchema,
        only=("id", "user.full_name", "user.phone"),
        dump_only=True,
    )
    review = fields.Nested("ReviewSchema", exclude=("service_request",), dump_only=True)


class ReviewSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Review
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    service_request_id = ma.Integer(required=True)

    rating = ma.Integer(
        required=True,
        validate=validate.Range(
            min=1, max=5, error="Rating must be between 1 and 5 stars."
        ),
    )
    comment = ma.String(
        required=False,
        allow_none=True,
        validate=validate.Length(
            min=1,
            max=500,
            error="Review comment must be between 1 and 500 characters.",
        ),
    )

    is_reported = ma.Boolean(dump_only=True)
    report_reason = ma.String(dump_only=True)
    created_at = ma.DateTime(dump_only=True)

    # Nested relationship
    service_request = fields.Nested(
        ServiceRequestSchema, exclude=("review",), dump_only=True
    )


# Initialize schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)
professional_profile_schema = ProfessionalProfileSchema()
professional_profiles_schema = ProfessionalProfileSchema(many=True)
customer_profile_schema = CustomerProfileSchema()
customer_profiles_schema = CustomerProfileSchema(many=True)
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)
service_request_schema = ServiceRequestSchema()
service_requests_schema = ServiceRequestSchema(many=True)
review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)
