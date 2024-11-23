import logging
from faker import Faker
from datetime import datetime, timedelta
import random
from . import db
from src.models import (
    User,
    UserRole,
    RequestStatus,
    ProfessionalProfile,
    CustomerProfile,
    Service,
    ServiceRequest,
    Review,
    ActivityLog,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()


def generate_valid_phone():
    """Generate a valid 10-digit phone number starting with a non-zero digit"""
    return f"{random.randint(1, 9)}" + "".join(
        [str(random.randint(0, 9)) for _ in range(9)]
    )


def generate_valid_pincode():
    """Generate a valid 6-digit PIN code not starting with 0"""
    return f"{random.randint(1, 9)}" + "".join(
        [str(random.randint(0, 9)) for _ in range(5)]
    )


def generate_valid_name():
    """Generate a valid full name with proper formatting"""
    name = fake.name()
    # Remove any characters that don't match our validation
    name = "".join(c for c in name if c.isalpha() or c in [" ", "-", "."])
    return name


def generate_valid_address():
    """Generate a valid address under 500 characters"""
    address = fake.address()
    return address[:499] if len(address) > 499 else address


def setup_database():
    """Initialize database with dummy data"""
    db.drop_all()
    logger.info("Dropped all tables.")

    db.create_all()
    logger.info("Created all tables.")

    create_dummy_data()
    logger.info("Populated database with dummy data.")


def create_dummy_data():
    """Create initial data"""
    # Create admin user
    admin = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        phone="9876543210",
        address="Admin Office, Main Street, Central District",
        pin_code="110001",
        role=UserRole.ADMIN,
        is_active=True,
    )
    admin.set_password("Admin@123")  # Strong password following validation rules
    db.session.add(admin)
    db.session.commit()
    logger.info("Created admin user")

    # Create services
    services = create_services()

    # Create professionals and customers
    professionals = create_professionals(services)
    customers = create_customers()

    # Create service requests and reviews
    create_requests_and_reviews(services, professionals, customers)

    db.session.commit()


def create_services():
    services = []
    service_data = [
        {
            "name": "AC Repair & Service",
            "price": 1500,
            "time": 120,  # 2 hours in minutes
            "description": "Professional AC repair and maintenance services including gas refill, component replacement, and thorough cleaning.",
        },
        {
            "name": "Plumbing Service",
            "price": 800,
            "time": 60,  # 1 hour in minutes
            "description": "Expert plumbing services for leak repairs, pipe installation, fixture mounting, and drainage solutions.",
        },
        {
            "name": "Electrical Work",
            "price": 1000,
            "time": 120,  # 2 hours
            "description": "Certified electrical services including wiring, installation, repairs, and safety inspections.",
        },
        {
            "name": "Carpentry",
            "price": 1200,
            "time": 180,  # 3 hours
            "description": "Professional carpentry services for furniture repair, custom woodwork, and installations.",
        },
        {
            "name": "House Painting",
            "price": 3000,
            "time": 480,  # 8 hours
            "description": "Complete house painting services with premium quality paints and professional finish.",
        },
    ]

    for data in service_data:
        service = Service(
            name=data["name"],
            description=data["description"],
            base_price=data["price"],
            time_required=data["time"],  # Stored in minutes
            is_active=True,
        )
        services.append(service)
        db.session.add(service)

    db.session.commit()
    logger.info(f"Created {len(services)} services")
    return services


def create_professionals(services):
    professionals = []

    service_descriptions = {
        "AC Repair & Service": "Certified AC technician with expertise in all major brands.",
        "Plumbing Service": "Licensed plumber specializing in residential plumbing systems.",
        "Electrical Work": "Certified electrician with focus on home electrical systems.",
        "Carpentry": "Skilled carpenter with experience in custom furniture and repairs.",
        "House Painting": "Professional painter specializing in interior and exterior painting.",
    }

    for i in range(5):
        # Select a service first to make matching description
        service = random.choice(services)

        username = f"pro{i+1}"
        email = f"pro{i+1}@service.com"

        # Create user with valid data
        user = User(
            username=username,
            email=email,
            full_name=generate_valid_name(),
            phone=generate_valid_phone(),
            address=generate_valid_address(),
            pin_code=generate_valid_pincode(),
            role=UserRole.PROFESSIONAL,
            is_active=True,
        )
        user.set_password(f"Pro@{i+1}123")  # Strong password following validation
        db.session.add(user)
        db.session.flush()

        # Create professional profile with valid data
        profile = ProfessionalProfile(
            user_id=user.id,
            service_type_id=service.id,
            experience_years=random.randint(2, 15),
            description=service_descriptions[service.name],
            is_verified=True,
            verification_documents="verification_docs.pdf",
            average_rating=round(random.uniform(4.0, 5.0), 1),  # Good initial ratings
        )
        professionals.append(profile)
        db.session.add(profile)

    db.session.commit()
    logger.info(f"Created {len(professionals)} professionals")
    return professionals


def create_customers():
    customers = []

    for i in range(10):
        username = f"customer{i+1}"
        email = f"customer{i+1}@email.com"

        # Create user with valid data
        user = User(
            username=username,
            email=email,
            full_name=generate_valid_name(),
            phone=generate_valid_phone(),
            address=generate_valid_address(),
            pin_code=generate_valid_pincode(),
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        user.set_password(f"Customer@{i+1}123")  # Strong password following validation
        db.session.add(user)
        db.session.flush()

        # Create customer profile
        profile = CustomerProfile(user_id=user.id)
        customers.append(profile)
        db.session.add(profile)

    db.session.commit()
    logger.info(f"Created {len(customers)} customers")
    return customers


def create_requests_and_reviews(services, professionals, customers):
    status_weights = [
        (RequestStatus.COMPLETED, 0.4),
        (RequestStatus.ASSIGNED, 0.3),
        (RequestStatus.REQUESTED, 0.3),
    ]

    for customer in customers:
        # Create 2-3 service requests per customer
        for _ in range(random.randint(2, 3)):
            service = random.choice(services)
            professional = random.choice(professionals)

            # Weight the status selection to have a good distribution
            status = random.choices(
                [s[0] for s in status_weights], weights=[s[1] for s in status_weights]
            )[0]

            # Create a timeline that makes sense
            base_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            request_date = base_date
            assignment_date = (
                base_date + timedelta(hours=2)
                if status != RequestStatus.REQUESTED
                else None
            )
            completion_date = (
                base_date + timedelta(days=1)
                if status == RequestStatus.COMPLETED
                else None
            )

            service_request = ServiceRequest(
                service_id=service.id,
                customer_id=customer.id,
                professional_id=professional.id
                if status != RequestStatus.REQUESTED
                else None,
                date_of_request=request_date,
                preferred_time=f"{random.randint(9, 17)}:00",  # Business hours
                description=f"Need {service.name} - {fake.sentence()}",
                status=status,
                date_of_assignment=assignment_date,
                date_of_completion=completion_date,
                remarks="Service completed successfully."
                if status == RequestStatus.COMPLETED
                else None,
            )
            db.session.add(service_request)
            db.session.flush()

            # Add review for completed requests
            if status == RequestStatus.COMPLETED:
                rating = random.randint(4, 5)  # Mostly positive reviews
                review = Review(
                    service_request_id=service_request.id,
                    rating=rating,
                    comment=f"{'Very satisfied' if rating == 5 else 'Good service'}. {fake.sentence()}",
                    is_reported=False,  # Start with no reported reviews
                )
                db.session.add(review)

                # Update professional's average rating
                prof_reviews = (
                    Review.query.join(ServiceRequest)
                    .filter(ServiceRequest.professional_id == professional.id)
                    .all()
                )
                total_ratings = sum(r.rating for r in prof_reviews) + rating
                professional.average_rating = round(
                    total_ratings / (len(prof_reviews) + 1), 1
                )

            # Create activity log for the request
            log = ActivityLog(
                user_id=customer.id,
                action="create_service_request",
                entity_type="service_request",
                entity_id=service_request.id,
                description=f"Created service request for {service.name}",
            )
            db.session.add(log)

    db.session.commit()
    logger.info("Created service requests, reviews, and activity logs")


if __name__ == "__main__":
    setup_database()
