from datetime import datetime

from marshmallow import Schema, ValidationError, fields, validates


class ExportRequestSchema(Schema):
    """Schema for export request parameters"""

    professional_id = fields.Int(required=False)
    start_date = fields.Str(required=False)
    end_date = fields.Str(required=False)

    @validates("start_date")
    def validate_start_date(self, value):
        try:
            if value:
                datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD")

    @validates("end_date")
    def validate_end_date(self, value):
        try:
            if value:
                end_date = datetime.strptime(value, "%Y-%m-%d")
                if end_date < datetime.strptime(
                    self.context.get("start_date", "2000-01-01"), "%Y-%m-%d"
                ):
                    raise ValidationError("End date must be after start date")
        except ValueError as e:
            if "must be after start date" in str(e):
                raise
            raise ValidationError("Invalid date format. Use YYYY-MM-DD")


export_request_schema = ExportRequestSchema()
