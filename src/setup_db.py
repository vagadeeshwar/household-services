import logging
from faker import Faker
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from . import db
from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    Service,
    ServiceRequest,
    Review,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()


def setup_database():
    """
    Drops all tables, recreates them, and populates the database with dummy data
    """
    # Drop all tables
    db.drop_all()
    logger.info("Dropped all tables.")

    # Create all tables
    db.create_all()
    logger.info("Created all tables.")

    # Insert dummy data
    create_dummy_data()
    logger.info("Populated database with dummy data.")


def create_dummy_data():
    """Orchestrates the dummy data creation process"""
    # Create admin user first
    create_admin_user()

    # Create other entities
    users = create_dummy_users()
    services = create_dummy_services()
    professionals = create_dummy_professionals(users["professional"], services)
    customers = create_dummy_customers(users["customer"])
    service_requests = create_dummy_service_requests(services, customers, professionals)
    create_dummy_reviews(service_requests)


def create_admin_user():
    """Creates the admin user"""
    admin = User(
        username="admin", email="admin@example.com", role="admin", is_active=True
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    logger.info("Admin user created.")


def create_dummy_users():
    """Creates dummy users with different roles"""
    users = {"professional": [], "customer": []}

    # Create 10 professional users
    for _ in range(10):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            role="professional",
            is_active=True,
            last_login=fake.date_time_this_month(),
        )
        user.set_password("password123")
        users["professional"].append(user)
        db.session.add(user)

    # Create 20 customer users
    for _ in range(20):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            role="customer",
            is_active=True,
            last_login=fake.date_time_this_month(),
        )
        user.set_password("password123")
        users["customer"].append(user)
        db.session.add(user)

    db.session.commit()
    logger.info("30 dummy users created.")
    return users


def create_dummy_services():
    """Creates dummy services"""
    services = []
    service_types = [
        {"name": "AC Repair", "time": "2 hours", "price": 1500},
        {"name": "Plumbing", "time": "1 hour", "price": 800},
        {"name": "Electrical Work", "time": "2 hours", "price": 1000},
        {"name": "Carpentry", "time": "3 hours", "price": 1200},
        {"name": "House Cleaning", "time": "4 hours", "price": 1000},
        {"name": "Painting", "time": "8 hours", "price": 3000},
        {"name": "Pest Control", "time": "2 hours", "price": 1500},
        {"name": "Gardening", "time": "3 hours", "price": 800},
    ]

    for service_type in service_types:
        service = Service(
            name=service_type["name"],
            description=fake.paragraph(),
            base_price=service_type["price"],
            time_required=service_type["time"],
            is_active=True,
        )
        services.append(service)
        db.session.add(service)

    db.session.commit()
    logger.info(f"{len(services)} services created.")
    return services


def create_dummy_professionals(users, services):
    """Creates dummy professional profiles"""
    professionals = []
    for user in users:
        service = fake.random_element(services)
        profile = ProfessionalProfile(
            user_id=user.id,
            full_name=fake.name(),
            phone=fake.numerify("##########"),
            experience_years=fake.random_int(min=1, max=20),
            description=fake.paragraph(),
            is_verified=fake.boolean(chance_of_getting_true=70),
            verification_documents="dummy_docs.pdf",
            service_type_id=service.id,
            average_rating=fake.random_int(min=3, max=5),
        )
        professionals.append(profile)
        db.session.add(profile)

    db.session.commit()
    logger.info(f"{len(professionals)} professional profiles created.")
    return professionals


def create_dummy_customers(users):
    """Creates dummy customer profiles"""
    customers = []
    for user in users:
        profile = CustomerProfile(
            user_id=user.id,
            full_name=fake.name(),
            phone=fake.numerify("##########"),
            address=fake.address(),
            pin_code=fake.numerify("######"),
        )
        customers.append(profile)
        db.session.add(profile)

    db.session.commit()
    logger.info(f"{len(customers)} customer profiles created.")
    return customers


def create_dummy_service_requests(services, customers, professionals):
    """Creates dummy service requests"""
    service_requests = []
    statuses = ["requested", "assigned", "in_progress", "completed", "closed"]

    for customer in customers:
        # Create 2-4 service requests per customer
        for _ in range(fake.random_int(min=2, max=4)):
            service = fake.random_element(services)
            professional = fake.random_element(professionals)
            status = fake.random_element(statuses)

            # Generate dates based on status
            request_date = fake.date_time_this_year()
            assignment_date = None
            completion_date = None

            if status in ["assigned", "in_progress", "completed", "closed"]:
                assignment_date = request_date + timedelta(days=1)
            if status in ["completed", "closed"]:
                completion_date = assignment_date + timedelta(days=1)

            service_request = ServiceRequest(
                service_id=service.id,
                customer_id=customer.id,
                professional_id=professional.id if status != "requested" else None,
                date_of_request=request_date,
                preferred_time=fake.time(),
                address=customer.address,
                pin_code=customer.pin_code,
                description=fake.paragraph(),
                status=status,
                date_of_assignment=assignment_date,
                date_of_completion=completion_date,
                remarks=fake.text() if status in ["completed", "closed"] else None,
            )
            service_requests.append(service_request)
            db.session.add(service_request)

    db.session.commit()
    logger.info(f"{len(service_requests)} service requests created.")
    return service_requests


def create_dummy_reviews(service_requests):
    """Creates dummy reviews for completed service requests"""
    reviews = []
    completed_requests = [req for req in service_requests if req.status == "closed"]

    for request in completed_requests:
        review = Review(
            service_request_id=request.id,
            rating=fake.random_int(min=1, max=5),
            comment=fake.paragraph(),
            is_reported=fake.boolean(chance_of_getting_true=10),
            report_reason=fake.text()
            if fake.boolean(chance_of_getting_true=10)
            else None,
        )
        reviews.append(review)
        db.session.add(review)

    db.session.commit()
    logger.info(f"{len(reviews)} reviews created.")
    return reviews
