from datetime import datetime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy.schema import CheckConstraint
from src.constants import (
    USER_ROLES,
    REQUEST_STATUSES,
    REQUEST_STATUS_REQUESTED,
    ActivityLogActions,
)


class TimestampMixin:
    """Mixin for created and updated timestamps"""

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class User(db.Model, TimestampMixin):
    """Base User Model for all types of users"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(
        db.String(10), CheckConstraint("length(phone) = 10"), nullable=False
    )
    pin_code = db.Column(
        db.String(6), CheckConstraint("length(pin_code) = 6"), nullable=False
    )
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)

    # Relationships with cascade
    professional_profile = relationship(
        "ProfessionalProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    customer_profile = relationship(
        "CustomerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(f"role IN {tuple(USER_ROLES)}", name="valid_role_types"),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class ProfessionalProfile(db.Model, TimestampMixin):
    """Profile for service professionals"""

    __tablename__ = "professional_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )
    description = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    verification_documents = db.Column(db.String(500))
    service_type_id = db.Column(
        db.Integer,
        db.ForeignKey("services.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    experience_years = db.Column(
        db.Integer, CheckConstraint("experience_years >= 0"), nullable=False
    )
    average_rating = db.Column(
        db.Float,
        CheckConstraint("average_rating >= 0 AND average_rating <= 5"),
        default=0.0,
    )

    # Relationships with cascade
    user = relationship("User", back_populates="professional_profile")
    service_type = relationship("Service", back_populates="professionals")
    service_requests = relationship(
        "ServiceRequest", back_populates="professional", cascade="all, delete-orphan"
    )


class CustomerProfile(db.Model, TimestampMixin):
    """Profile for customers"""

    __tablename__ = "customer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Relationships with cascade
    user = relationship("User", back_populates="customer_profile")
    service_requests = relationship(
        "ServiceRequest", back_populates="customer", cascade="all, delete-orphan"
    )


class Service(db.Model, TimestampMixin):
    """Service types available on the platform"""

    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships with cascade
    professionals = relationship(
        "ProfessionalProfile",
        back_populates="service_type",
        cascade="all, delete-orphan",
    )
    service_requests = relationship(
        "ServiceRequest", back_populates="service", cascade="all, delete-orphan"
    )


class ServiceRequest(db.Model, TimestampMixin):
    """Service requests from customers"""

    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(
        db.Integer,
        db.ForeignKey("services.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer_profiles.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    professional_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "professional_profiles.id", ondelete="SET NULL", onupdate="CASCADE"
        ),
    )

    date_of_request = db.Column(db.DateTime, nullable=False)
    preferred_time = db.Column(db.String(50))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default=REQUEST_STATUS_REQUESTED)
    date_of_assignment = db.Column(db.DateTime)
    date_of_completion = db.Column(db.DateTime)
    remarks = db.Column(db.Text)

    # Relationships with cascade
    service = relationship("Service", back_populates="service_requests")
    customer = relationship("CustomerProfile", back_populates="service_requests")
    professional = relationship(
        "ProfessionalProfile", back_populates="service_requests"
    )
    review = relationship(
        "Review",
        back_populates="service_request",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            f"status IN {tuple(REQUEST_STATUSES)}", name="valid_status_types"
        ),
    )


class Review(db.Model, TimestampMixin):
    """Reviews for completed services"""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(
        db.Integer,
        db.ForeignKey("service_requests.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )
    rating = db.Column(
        db.Integer, CheckConstraint("rating >= 1 AND rating <= 5"), nullable=False
    )
    comment = db.Column(db.Text)
    is_reported = db.Column(db.Boolean, default=False)
    report_reason = db.Column(db.Text)

    # Relationships with cascade
    service_request = relationship("ServiceRequest", back_populates="review")


class ActivityLog(db.Model, TimestampMixin):
    """Audit trail for important activities"""

    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE")
    )
    action = db.Column(
        db.String(50),
        nullable=False,
    )
    description = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.CheckConstraint(
            f"action IN {tuple(ActivityLogActions.get_all_actions())}",
            name="valid_action_types",
        ),
    )

    def __repr__(self):
        return f"<ActivityLog {self.action} by User {self.user_id}>"
