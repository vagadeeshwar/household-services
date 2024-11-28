from marshmallow import fields, Schema, validate


class ActivityLogQuerySchema(Schema):
    """Schema for activity log query parameters"""

    action = fields.Str(required=False)
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
    action = fields.Str(required=True)
    description = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)


class DetailedStatsQuerySchema(Schema):
    """Schema for detailed statistics query parameters"""

    stat_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                # Admin
                "pending_verifications",
                "reported_reviews",
                "recent_professionals",
                "recent_customers",
                "recent_requests",
                # Professional
                "pending_requests",
                "active_requests",
                "completed_requests",
                "my_reviews",
                "reported_reviews",
                # Customer
                "pending_requests",
                "active_requests",
                "completed_requests",
                "my_reviews",
                "available_services",
            ]
        ),
    )
    start_date = fields.DateTime(required=False)
    end_date = fields.DateTime(required=False)
    page = fields.Int(required=False, missing=1)
    per_page = fields.Int(required=False, missing=10)


class DashboardStatsSchema(Schema):
    """Schema for dashboard statistics"""

    # Admin stats
    total_professionals = fields.Int(required=False)
    verified_professionals = fields.Int(required=False)
    total_customers = fields.Int(required=False)
    active_customers = fields.Int(required=False)
    pending_verifications = fields.Int(required=False)
    reported_reviews = fields.Int(required=False)
    service_requests = fields.Dict(
        keys=fields.Str(), values=fields.Int(), required=False
    )

    # Professional stats
    profile_status = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False)
    reviews = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False)

    # Customer stats
    recent_services = fields.Int(required=False)
    reviews_given = fields.Int(required=False)


activity_logs_schema = ActivityLogSchema(many=True)
activity_log_query_schema = ActivityLogQuerySchema()

detailed_stats_query_schema = DetailedStatsQuerySchema()
dashboard_stats_schema = DashboardStatsSchema()
