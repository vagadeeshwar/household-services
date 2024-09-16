from datetime import datetime
import enum
from . import db  # Import db from the centralized init file
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    sponsor_profile = db.relationship(
        "Sponsor",
        backref="user",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
    )
    influencer_profile = db.relationship(
        "Influencer",
        backref="user",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Sponsor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    company_name = db.Column(db.String(100), nullable=False, unique=True)
    industry = db.Column(db.String(50))
    budget = db.Column(db.Float)
    campaigns = db.relationship(
        "Campaign", backref="sponsor", lazy=True, cascade="all, delete-orphan"
    )


class Influencer(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    niche = db.Column(db.String(50))
    reach = db.Column(db.Integer)
    ad_requests = db.relationship(
        "AdRequest", backref="influencer", lazy=True, cascade="all, delete-orphan"
    )


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    visibility = db.Column(db.String(10))
    goals = db.Column(db.Text)
    sponsor_id = db.Column(db.Integer, db.ForeignKey("sponsor.id"), nullable=False)
    ad_requests = db.relationship(
        "AdRequest", backref="campaign", lazy=True, cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.CheckConstraint("start_date <= end_date", name="check_start_date_end_date"),
        db.UniqueConstraint(
            "name", "sponsor_id", name="unique_campaign_name_per_sponsor"
        ),
    )


class AdRequestStatus(enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"), nullable=False)
    influencer_id = db.Column(
        db.Integer, db.ForeignKey("influencer.id"), nullable=False
    )
    messages = db.Column(db.Text)
    requirements = db.Column(db.Text)
    payment_amount = db.Column(db.Float)
    status = db.Column(
        db.Enum(AdRequestStatus), default=AdRequestStatus.PENDING, nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
