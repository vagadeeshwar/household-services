from marshmallow import Schema, fields, validate, validates

from src.constants import ActivityLogActions
from src.schemas.base import BaseSchema, BaseUserSchema


class AdminAccountSchema(BaseUserSchema):
    """Schema for admin account creation"""

    pass


class BlockUserSchema(BaseSchema):
    """Schema for blocking user requests"""

    reason = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)


class PasswordUpdateSchema(BaseSchema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True)

    @validates("new_password")
    def validate_new_password(self, value):
        self.validate_password(value)


class DeleteAccountSchema(BaseSchema):
    password = fields.Str(required=True)

    from marshmallow import Schema, fields, validate



actions = ActivityLogActions.get_all_actions()
actions.append("all")


class ActivityLogQuerySchema(Schema):
    """Schema for activity log query parameters"""

    action = fields.Str(required=False, validate=validate.OneOf(actions))
    user_id = fields.Int(required=False)
    start_date = fields.DateTime(required=False)
    end_date = fields.DateTime(required=False)
    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)


class ActivityLogSchema(Schema):
    """Schema for activity log output"""

    id = fields.Int(dump_only=True)
    user_id = fields.Int(allow_none=True)
    entity_id = fields.Int(allow_none=True)
    action = fields.Str(required=True, validate=validate.OneOf(actions))
    description = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)


activity_logs_schema = ActivityLogSchema(many=True)
activity_log_query_schema = ActivityLogQuerySchema()


admin_output_schema = AdminAccountSchema()
block_user_schema = BlockUserSchema()
password_update_schema = PasswordUpdateSchema()
delete_account_schema = DeleteAccountSchema()
