from datetime import datetime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from enum import Enum
from sqlalchemy.schema import CheckConstraint


class TimestampMixin:
    """Mixin for created and updated timestamps"""

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class RequestStatus(Enum):
    REQUESTED = "requested"
    ASSIGNED = "assigned"
    COMPLETED = "completed"


class UserRole(Enum):
    ADMIN = "admin"
    PROFESSIONAL = "professional"
    CUSTOMER = "customer"


class User(db.Model, TimestampMixin):
    """Base User Model for all types of users"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(
        db.String(10),
        CheckConstraint("length(phone) = 10"),
        nullable=False,
    )
    pin_code = db.Column(
        db.String(6),
        CheckConstraint("length(pin_code) = 6"),
        nullable=False,
    )

    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)

    # Relationships based on role
    professional_profile = relationship(
        "ProfessionalProfile", back_populates="user", uselist=False
    )
    customer_profile = relationship(
        "CustomerProfile", back_populates="user", uselist=False
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
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )

    description = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    verification_documents = db.Column(db.String(500))  # URLs to documents
    service_type_id = db.Column(
        db.Integer, db.ForeignKey("services.id"), nullable=False
    )
    experience_years = db.Column(
        db.Integer,
        CheckConstraint("experience_years >= 0"),
        nullable=False,
    )
    average_rating = db.Column(
        db.Float,
        CheckConstraint("average_rating >= 0 AND average_rating <= 5"),
        default=0.0,
    )
    # Relationships
    user = relationship("User", back_populates="professional_profile")
    service_type = relationship("Service", back_populates="professionals")
    service_requests = relationship("ServiceRequest", back_populates="professional")


class CustomerProfile(db.Model, TimestampMixin):
    """Profile for customers"""

    __tablename__ = "customer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="customer_profile")
    service_requests = relationship("ServiceRequest", back_populates="customer")


class Service(db.Model, TimestampMixin):
    """Service types available on the platform"""

    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=False)  # e.g., "2 hours", "1 day"
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    professionals = relationship("ProfessionalProfile", back_populates="service_type")
    service_requests = relationship("ServiceRequest", back_populates="service")


class ServiceRequest(db.Model, TimestampMixin):
    """Service requests from customers"""

    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customer_profiles.id"), nullable=False
    )
    professional_id = db.Column(db.Integer, db.ForeignKey("professional_profiles.id"))

    # Request details
    date_of_request = db.Column(db.DateTime, nullable=False)
    preferred_time = db.Column(db.String(50))

    description = db.Column(db.Text)

    # Status tracking
    status = db.Column(
        db.Enum(RequestStatus), nullable=False, default=RequestStatus.REQUESTED
    )
    date_of_assignment = db.Column(db.DateTime)
    date_of_completion = db.Column(db.DateTime)
    remarks = db.Column(db.Text)

    # Relationships
    service = relationship("Service", back_populates="service_requests")
    customer = relationship("CustomerProfile", back_populates="service_requests")
    professional = relationship(
        "ProfessionalProfile", back_populates="service_requests"
    )
    review = relationship("Review", back_populates="service_request", uselist=False)


class Review(db.Model, TimestampMixin):
    """Reviews for completed services"""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(
        db.Integer, db.ForeignKey("service_requests.id"), unique=True, nullable=False
    )
    rating = db.Column(
        db.Integer,
        CheckConstraint("rating >= 1 AND rating <= 5"),
        nullable=False,
    )
    comment = db.Column(db.Text)
    is_reported = db.Column(db.Boolean, default=False)
    report_reason = db.Column(db.Text)

    # Relationships
    service_request = relationship("ServiceRequest", back_populates="review")


class ActivityLog(db.Model, TimestampMixin):
    """Audit trail for important activities"""

    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(
        db.String(50), nullable=False
    )  # e.g., 'service_request', 'review'
    entity_id = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
