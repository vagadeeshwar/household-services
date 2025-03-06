from marshmallow import Schema, fields


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class TokenSchema(Schema):
    token = fields.Str(required=True)


login_schema = LoginSchema()
token_schema = TokenSchema()
