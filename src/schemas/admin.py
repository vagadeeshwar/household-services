from marshmallow import fields, Schema


class DashboardStatsSchema(Schema):
    """Schema for dashboard statistics output"""

    total_professionals = fields.Int(required=True)
    verified_professionals = fields.Int(required=True)
    total_customers = fields.Int(required=True)
    active_customers = fields.Int(required=True)
    pending_verifications = fields.Int(required=True)
    reported_reviews = fields.Int(required=True)
    service_requests = fields.Dict(
        keys=fields.Str(), values=fields.Int(), required=True
    )


dashboard_stats_schema = DashboardStatsSchema()
