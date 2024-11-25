from marshmallow import fields, validate, Schema
from .base import BaseSchema
from .service import ServiceOutputSchema
from .user import CustomerOutputSchema, ProfessionalOutputSchema


class ServiceRequestInputSchema(BaseSchema):
    service_id = fields.Int(required=True)
    preferred_time = fields.Str()
    description = fields.Str(validate=validate.Length(max=1000))


class ServiceRequestOutputSchema(Schema):
    id = fields.Int(required=True)
    service = fields.Nested(ServiceOutputSchema, dump_only=True)
    customer = fields.Nested(CustomerOutputSchema, dump_only=True)
    professional = fields.Nested(
        ProfessionalOutputSchema, dump_only=True, allow_none=True
    )
    date_of_request = fields.DateTime(required=True)
    preferred_time = fields.Str(allow_none=True)
    status = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    date_of_assignment = fields.DateTime(allow_none=True)
    date_of_completion = fields.DateTime(allow_none=True)
    remarks = fields.Str(allow_none=True)


class ReviewInputSchema(BaseSchema):
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(validate=validate.Length(max=1000))


class ReviewOutputSchema(Schema):
    id = fields.Int(required=True)
    rating = fields.Int(required=True)
    comment = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)
    service_request_id = fields.Int(required=True)


service_request_schema = ServiceRequestOutputSchema()
service_requests_schema = ServiceRequestOutputSchema(many=True)
review_schema = ReviewOutputSchema()
reviews_schema = ReviewOutputSchema(many=True)
