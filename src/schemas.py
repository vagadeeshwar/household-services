from marshmallow import fields, validate, validates, ValidationError
from models import User, ProfessionalProfile, CustomerProfile, Service, ServiceRequest, Review
from . import ma

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(required=True, validate=validate.Length(min=3, max=80))
    email = ma.Email(required=True)
    role = ma.String(required=True, validate=validate.OneOf(['admin', 'professional', 'customer']))
    password = ma.String(load_only=True, required=True, validate=validate.Length(min=6))
    is_active = ma.Boolean(dump_only=True)
    created_at = ma.DateTime(dump_only=True)
    updated_at = ma.DateTime(dump_only=True)
    last_login = ma.DateTime(dump_only=True)

class ProfessionalProfileSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ProfessionalProfile
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)
    full_name = ma.String(required=True, validate=validate.Length(min=2, max=100))
    phone = ma.String(required=True, validate=validate.Length(equal=10))
    experience_years = ma.Integer(required=True, validate=validate.Range(min=0, max=50))
    description = ma.String()
    is_verified = ma.Boolean(dump_only=True)
    verification_documents = ma.String()
    service_type_id = ma.Integer(required=True)
    average_rating = ma.Float(dump_only=True)
    created_at = ma.DateTime(dump_only=True)
    
    # Nested relationships
    user = fields.Nested('UserSchema', only=('id', 'username', 'email'), dump_only=True)
    service_type = fields.Nested('ServiceSchema', only=('id', 'name'), dump_only=True)

class CustomerProfileSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CustomerProfile
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)
    full_name = ma.String(required=True, validate=validate.Length(min=2, max=100))
    phone = ma.String(required=True, validate=validate.Length(equal=10))
    address = ma.String(required=True)
    pin_code = ma.String(required=True, validate=validate.Length(equal=6))
    created_at = ma.DateTime(dump_only=True)

    # Nested relationships
    user = fields.Nested('UserSchema', only=('id', 'username', 'email'), dump_only=True)

class ServiceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Service
        load_instance = True

    id = ma.auto_field(dump_only=True)
    name = ma.String(required=True, validate=validate.Length(min=2, max=100))
    description = ma.String(required=True)
    base_price = ma.Float(required=True, validate=validate.Range(min=0))
    time_required = ma.String(required=True)
    is_active = ma.Boolean()
    created_at = ma.DateTime(dump_only=True)

    professionals = fields.Nested('ProfessionalProfileSchema', many=True, only=('id', 'full_name', 'average_rating'), dump_only=True)

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
    address = ma.String(required=True)
    pin_code = ma.String(required=True, validate=validate.Length(equal=6))
    description = ma.String()
    status = ma.String(validate=validate.OneOf(['requested', 'assigned', 'in_progress', 'completed', 'closed']))
    date_of_assignment = ma.DateTime(dump_only=True)
    date_of_completion = ma.DateTime(dump_only=True)
    remarks = ma.String()
    created_at = ma.DateTime(dump_only=True)

    # Nested relationships
    service = fields.Nested('ServiceSchema', only=('id', 'name', 'base_price'), dump_only=True)
    customer = fields.Nested('CustomerProfileSchema', only=('id', 'full_name', 'phone'), dump_only=True)
    professional = fields.Nested('ProfessionalProfileSchema', only=('id', 'full_name', 'phone'), dump_only=True)
    review = fields.Nested('ReviewSchema', exclude=('service_request',), dump_only=True)

class ReviewSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Review
        load_instance = True
        include_fk = True

    id = ma.auto_field(dump_only=True)
    service_request_id = ma.Integer(required=True)
    rating = ma.Integer(required=True, validate=validate.Range(min=1, max=5))
    comment = ma.String()
    is_reported = ma.Boolean(dump_only=True)
    report_reason = ma.String(dump_only=True)
    created_at = ma.DateTime(dump_only=True)

    # Nested relationship
    service_request = fields.Nested('ServiceRequestSchema', exclude=('review',), dump_only=True)

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