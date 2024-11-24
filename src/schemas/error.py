from marshmallow import fields, Schema


class ErrorOutputSchema(Schema):
    status = fields.Str(required=True)
    status_code = fields.Int(required=True)
    detail = fields.Str(required=True)
    error_type = fields.Str(required=True)
