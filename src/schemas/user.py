from marshmallow import fields, validates

from src.schemas.base import BaseSchema, BaseUserSchema


class AdminAccountSchema(BaseUserSchema):
    """Schema for admin account creation"""

    pass


class BlockUserSchema(BaseSchema):
    """Schema for blocking user requests"""

    reason = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)


class PasswordUpdateInputSchema(BaseSchema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True)

    @validates("new_password")
    def validate_new_password(self, value):
        self.validate_password(value)


class DeleteAccountInputSchema(BaseSchema):
    password = fields.Str(required=True)


admin_output_schema = AdminAccountSchema()
block_user_schema = BlockUserSchema()
password_update_schema = PasswordUpdateInputSchema()
delete_account_schema = DeleteAccountInputSchema()
