from marshmallow import fields, Schema


class LoginInputSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class TokenOutputSchema(Schema):
    token = fields.Str(required=True)


login_schema = LoginInputSchema()
token_schema = TokenOutputSchema()
