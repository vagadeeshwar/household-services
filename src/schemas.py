from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from .models import AdRequestStatus, Sponsor, Influencer, Campaign
from datetime import datetime

# User Schema
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=[validate.Length(min=3, max=80)])
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True, validate=[validate.Length(min=6)])
    role = fields.Str(required=True, validate=validate.OneOf(["admin", "sponsor", "influencer"]))
    created_at = fields.DateTime(dump_only=True, default=datetime.utcnow)
    updated_at = fields.DateTime(dump_only=True, default=datetime.utcnow)

# Sponsor Schema
class SponsorSchema(Schema):
    id = fields.Int(dump_only=True)
    company_name = fields.Str(required=True, validate=[validate.Length(min=3, max=100)])
    industry = fields.Str(validate=validate.Length(max=50))
    budget = fields.Float()

    # Nested field to include user data
    user = fields.Nested(UserSchema, dump_only=True)

# Influencer Schema
class InfluencerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=[validate.Length(min=3, max=100)])
    category = fields.Str(validate=[validate.Length(max=50)])
    niche = fields.Str(validate=[validate.Length(max=50)])
    reach = fields.Int()

    # Nested field to include user data
    user = fields.Nested(UserSchema, dump_only=True)

# Campaign Schema
class CampaignSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=[validate.Length(min=3, max=100)])
    description = fields.Str()
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    budget = fields.Float()
    visibility = fields.Str(validate=validate.OneOf(["public", "private"]))
    goals = fields.Str()
    sponsor_id = fields.Int(required=True)

    # Foreign key validation: Ensure sponsor_id exists
    @validates('sponsor_id')
    def validate_sponsor_id(self, value):
        sponsor = Sponsor.query.get(value)
        if sponsor is None:
            raise ValidationError(f"Sponsor with id {value} does not exist.")

    # Custom validation for dates
    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data["start_date"] > data["end_date"]:
            raise ValidationError("start_date must be before or equal to end_date")

    # Nested field to include sponsor data
    sponsor = fields.Nested(SponsorSchema, dump_only=True)

# AdRequest Schema
class AdRequestSchema(Schema):
    id = fields.Int(dump_only=True)
    messages = fields.Str()
    requirements = fields.Str()
    payment_amount = fields.Float()
    status = fields.Str(required=True, validate=validate.OneOf([status.value for status in AdRequestStatus]))
    campaign_id = fields.Int(required=True)
    influencer_id = fields.Int(required=True)

    # Foreign key validation: Ensure campaign_id exists
    @validates('campaign_id')
    def validate_campaign_id(self, value):
        if not Campaign.query.get(value):
            raise ValidationError(f"Campaign with id {value} does not exist.")

    # Foreign key validation: Ensure influencer_id exists
    @validates('influencer_id')
    def validate_influencer_id(self, value):
        if not Influencer.query.get(value):
            raise ValidationError(f"Influencer with id {value} does not exist.")

    created_at = fields.DateTime(dump_only=True, default=datetime.utcnow)
    updated_at = fields.DateTime(dump_only=True, default=datetime.utcnow)

    # Nested fields to include campaign and influencer data
    campaign = fields.Nested(CampaignSchema, dump_only=True)
    influencer = fields.Nested(InfluencerSchema, dump_only=True)
