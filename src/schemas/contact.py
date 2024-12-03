from marshmallow import fields, Schema, validate

class ContactFormSchema(Schema):
    """Schema for contact form submissions"""
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    subject = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    message = fields.Str(required=True, validate=validate.Length(min=10, max=2000))

contact_form_schema = ContactFormSchema()