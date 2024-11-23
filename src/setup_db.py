import logging
from faker import Faker
from datetime import datetime, timedelta
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
        address="Admin Office, Main Street",
        pin_code="123456",
        role=UserRole.ADMIN,
        is_active=True,
    )
    admin.set_password("admin123")
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
        {"name": "AC Repair", "price": 1500, "time": "2 hours"},
        {"name": "Plumbing", "price": 800, "time": "1 hour"},
        {"name": "Electrical", "price": 1000, "time": "2 hours"},
        {"name": "Carpentry", "price": 1200, "time": "3 hours"},
        {"name": "Painting", "price": 3000, "time": "8 hours"},
    ]

    for data in service_data:
        service = Service(
            name=data["name"],
            description=fake.paragraph(),
            base_price=data["price"],
            time_required=data["time"],
            is_active=True,
        )
        services.append(service)
        db.session.add(service)

    db.session.commit()
    logger.info(f"Created {len(services)} services")
    return services


def create_professionals(services):
    professionals = []

    for i in range(5):
        # Create user first
        user = User(
            username=f"pro{i+1}",
            email=f"pro{i+1}@example.com",
            full_name=fake.name(),
            phone=fake.numerify("##########"),
            address=fake.address(),
            pin_code=fake.numerify("######"),
            role=UserRole.PROFESSIONAL,
            is_active=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()  # Commit to get user.id

        # Create professional profile
        profile = ProfessionalProfile(
            user_id=user.id,
            service_type_id=fake.random_element(services).id,
            experience_years=fake.random_int(min=1, max=20),
            description=fake.paragraph(),
            is_verified=fake.boolean(chance_of_getting_true=70),
            verification_documents="dummy_docs.pdf",
            average_rating=fake.random_int(min=3, max=5),
        )
        professionals.append(profile)
        db.session.add(profile)

    db.session.commit()
    logger.info(f"Created {len(professionals)} professionals")
    return professionals


def create_customers():
    customers = []

    for i in range(10):
        # Create user first
        user = User(
            username=f"customer{i+1}",
            email=f"customer{i+1}@example.com",
            full_name=fake.name(),
            phone=fake.numerify("##########"),
            address=fake.address(),
            pin_code=fake.numerify("######"),
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()  # Commit to get user.id

        # Create customer profile
        profile = CustomerProfile(user_id=user.id)
        customers.append(profile)
        db.session.add(profile)

    db.session.commit()
    logger.info(f"Created {len(customers)} customers")
    return customers


def create_requests_and_reviews(services, professionals, customers):
    for customer in customers:
        for _ in range(fake.random_int(min=1, max=3)):
            service = fake.random_element(services)
            professional = fake.random_element(professionals)
            status = fake.random_element(list(RequestStatus))

            request_date = fake.date_time_this_year()

            service_request = ServiceRequest(
                service_id=service.id,
                customer_id=customer.id,
                professional_id=professional.id
                if status != RequestStatus.REQUESTED
                else None,
                date_of_request=request_date,
                preferred_time=fake.time(),
                description=fake.paragraph(),
                status=status,
                date_of_assignment=request_date + timedelta(hours=1)
                if status != RequestStatus.REQUESTED
                else None,
                date_of_completion=request_date + timedelta(days=1)
                if status == RequestStatus.COMPLETED
                else None,
                remarks=fake.text() if status == RequestStatus.COMPLETED else None,
            )
            db.session.add(service_request)
            db.session.commit()  # Commit to get service_request.id

            # Add review for completed requests
            if status == RequestStatus.COMPLETED:
                review = Review(
                    service_request_id=service_request.id,  # Now we have a valid ID
                    rating=fake.random_int(min=1, max=5),
                    comment=fake.paragraph(),
                    is_reported=fake.boolean(chance_of_getting_true=10),
                    report_reason=fake.text()
                    if fake.boolean(chance_of_getting_true=10)
                    else None,
                )
                db.session.add(review)
                db.session.commit()

    logger.info("Created service requests and reviews")
