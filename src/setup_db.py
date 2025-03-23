import logging
import os
import random
import uuid
from datetime import datetime, time, timedelta, timezone

from faker import Faker

from src import db
from src.constants import (
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_COMPLETED,
    REQUEST_STATUS_CREATED,
    USER_ROLE_ADMIN,
    USER_ROLE_CUSTOMER,
    USER_ROLE_PROFESSIONAL,
    ActivityLogActions,
)
from src.models import (
    ActivityLog,
    CustomerProfile,
    ProfessionalProfile,
    Review,
    Service,
    ServiceRequest,
    User,
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


def create_activity_log(user_id, action, entity_id=None, description=None):
    """Helper function to create activity logs"""
    log = ActivityLog(
        user_id=user_id,
        action=action,
        entity_id=entity_id,
        description=description or f"Action: {action}",
    )
    db.session.add(log)
    return log


def setup_database():
    """Initialize database with dummy data"""
    try:
        db.drop_all()
        logger.info("Dropped all tables.")

        db.create_all()
        logger.info("Created all tables.")

        create_dummy_data()
        logger.info("Populated database with dummy data.")

    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        db.session.rollback()
        raise


def create_dummy_data():
    """Create initial data"""
    try:
        # Create admin user
        admin = User(
            username="admin",
            email="vagadeeshwarganesan@gmail.com",
            full_name="Admin User",
            phone="9876543210",
            address="Admin Office, Main Street, Central District",
            pin_code="110001",
            role=USER_ROLE_ADMIN,
            is_active=True,
            last_login=datetime.now(timezone.utc),
        )
        admin.set_password("Admin@123")
        db.session.add(admin)
        db.session.flush()

        create_activity_log(
            admin.id,
            ActivityLogActions.USER_REGISTER,
            admin.id,
            "Admin account created during system initialization",
        )

        # Log admin login
        create_activity_log(
            admin.id, ActivityLogActions.USER_LOGIN, admin.id, "Initial admin login"
        )

        db.session.commit()
        logger.info("Created admin user")

        # Create services
        services = create_services(admin.id)
        professionals = create_professionals(services, admin.id)
        customers = create_customers()
        create_requests_and_reviews(services, professionals, customers, admin.id)

        # Final commit
        db.session.commit()
        logger.info("Successfully completed database setup")

    except Exception as e:
        logger.error(f"Error in create_dummy_data: {str(e)}")
        db.session.rollback()
        raise


def create_professionals(services, admin_id):
    professionals = []
    verification_doc_template = "verification_doc_{uuid}.pdf"
    doc_directory = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "static/uploads/verification_docs"
    )

    # Clear existing files and create directory
    clear_static_directory()
    os.makedirs(doc_directory, exist_ok=True)

    service_descriptions = {
        "AC Repair & Service": "Certified AC technician with expertise in all major brands. HVAC certified with experience in split and window units.",
        "Plumbing Service": "Licensed plumber specializing in residential plumbing systems. Expertise in modern plumbing technologies.",
        "Electrical Work": "Certified electrician with focus on home electrical systems. Licensed for residential and commercial work.",
        "Carpentry": "Skilled carpenter with experience in custom furniture and repairs. Specializing in wooden furniture restoration.",
        "House Painting": "Professional painter specializing in interior and exterior painting. Expertise in textured finishes.",
        "Appliance Repair": "Certified appliance technician with multi-brand expertise. Specialized in household appliances.",
        "Home Cleaning": "Professional cleaner with expertise in deep cleaning and sanitization. Trained in modern cleaning methods.",
    }

    verification_statuses = [
        ("rejected", "Insufficient experience documentation"),
        ("pending", "Awaiting additional certifications"),
        ("verified", "All documents verified successfully"),
        ("blocked", "Multiple customer complaints"),
        ("resubmitted", "Updated documents after initial rejection"),
    ]

    user = User(
        username="shubhaganesan",
        email="shubhaganesan@gmail.com",
        full_name=generate_valid_name(),
        phone=generate_valid_phone(),
        address=generate_valid_address(),
        pin_code=generate_valid_pincode(),
        role=USER_ROLE_PROFESSIONAL,
        is_active=0,
        last_login=datetime.now(timezone.utc)
        - timedelta(days=90)
        - timedelta(days=random.randint(0, 30)),
    )
    user.set_password("Shubhaganesan@123")
    db.session.add(user)
    db.session.flush()

    doc_filename = verification_doc_template.format(uuid=uuid.uuid4().hex[:8])
    doc_path = os.path.join(doc_directory, doc_filename)
    with open(doc_path, "w") as f:
        f.write("Verification documents for shubhaganesan\n")
        f.write("Service Type: AC Repair & Service\n")
        f.write(f"Experience: {random.randint(2, 15)} years\n")
        f.write("Documents included:\n")
        f.write("1. Identity Proof\n")
        f.write("2. Address Proof\n")
        f.write("3. Professional Certification\n")

    profile = ProfessionalProfile(
        user_id=user.id,
        service_type_id=1,
        experience_years=random.randint(2, 15),
        description="hi",
        is_verified=False,  # Start with unverified status
        verification_documents=doc_filename,
        average_rating=None,  # Initially no rating
    )
    db.session.add(profile)
    db.session.flush()

    try:
        base_date = datetime.now(timezone.utc) - timedelta(days=90)

        for i in range(10):  # Increased number of professionals
            service = random.choice(services)
            username = f"pro{i + 1}"
            email = f"pro{i + 1}@service.com"
            is_active = random.random() < 0.8  # 80% chance of being active

            # Create user with initial pending status
            user = User(
                username=username,
                email=email,
                full_name=generate_valid_name(),
                phone=generate_valid_phone(),
                address=generate_valid_address(),
                pin_code=generate_valid_pincode(),
                role=USER_ROLE_PROFESSIONAL,
                is_active=is_active,
                last_login=base_date - timedelta(days=random.randint(0, 30)),
            )
            user.set_password(f"Pro@{i + 1}123")
            db.session.add(user)
            db.session.flush()

            # Initial registration log
            create_activity_log(
                user.id,
                ActivityLogActions.USER_REGISTER,
                user.id,
                f"Professional account created: {username}",
            )

            # Create and save dummy verification document
            doc_filename = verification_doc_template.format(uuid=uuid.uuid4().hex[:8])
            doc_path = os.path.join(doc_directory, doc_filename)
            with open(doc_path, "w") as f:
                f.write(f"Verification documents for {username}\n")
                f.write(f"Service Type: {service.name}\n")
                f.write(f"Experience: {random.randint(2, 15)} years\n")
                f.write("Documents included:\n")
                f.write("1. Identity Proof\n")
                f.write("2. Address Proof\n")
                f.write("3. Professional Certification\n")
                f.write("4. Experience Letters\n")

            # Create professional profile
            profile = ProfessionalProfile(
                user_id=user.id,
                service_type_id=service.id,
                experience_years=random.randint(2, 15),
                description=service_descriptions[service.name],
                is_verified=is_active,  # Start with unverified status
                verification_documents=doc_filename,
                average_rating=None,  # Initially no rating
            )
            db.session.add(profile)
            db.session.flush()

            # Simulate document updates and verification process
            current_date = base_date
            status_history = random.sample(verification_statuses, random.randint(2, 4))

            for status, reason in status_history:
                current_date += timedelta(days=random.randint(1, 5))

                if status == "rejected":
                    create_activity_log(
                        admin_id,
                        ActivityLogActions.PROFESSIONAL_DOCUMENT_UPDATE,
                        profile.id,
                        f"Verification rejected for {username}: {reason}",
                    )
                    user.is_active = False
                    profile.is_verified = False

                elif status == "resubmitted":
                    # Simulate document update
                    new_doc_filename = verification_doc_template.format(
                        uuid=uuid.uuid4().hex[:8]
                    )
                    new_doc_path = os.path.join(doc_directory, new_doc_filename)
                    with open(new_doc_path, "w") as f:
                        f.write(f"Updated verification documents for {username}\n")
                        f.write("Additional documents included\n")

                    # Update profile with new document
                    profile.verification_documents = new_doc_filename
                    create_activity_log(
                        user.id,
                        ActivityLogActions.PROFESSIONAL_DOCUMENT_UPDATE,
                        profile.id,
                        f"Updated verification documents: {reason}",
                    )

                elif status == "verified":
                    profile.is_verified = True
                    user.is_active = True
                    create_activity_log(
                        admin_id,
                        ActivityLogActions.PROFESSIONAL_VERIFY,
                        profile.id,
                        f"Verified professional {username}: {reason}",
                    )

                elif status == "blocked":
                    user.is_active = False
                    user.is_verified = True
                    create_activity_log(
                        admin_id,
                        ActivityLogActions.PROFESSIONAL_BLOCK,
                        profile.id,
                        f"Blocked professional {username}: {reason}",
                    )

                    # Simulate unblock after some time
                    if random.random() < 0.4:
                        current_date += timedelta(days=random.randint(10, 30))
                        user.is_active = True
                        create_activity_log(
                            admin_id,
                            ActivityLogActions.PROFESSIONAL_UNBLOCK,
                            profile.id,
                            f"Unblocked professional {username}: Completed necessary improvements",
                        )

            # Simulate service type changes for some professionals
            if random.random() < 0.3:
                new_service = random.choice([s for s in services if s.id != service.id])
                profile.service_type_id = new_service.id
                create_activity_log(
                    user.id,
                    ActivityLogActions.PROFESSIONAL_SERVICE_UPDATE,
                    profile.id,
                    f"Changed service type from {service.name} to {new_service.name}",
                )

            # Simulate profile updates
            for _ in range(random.randint(0, 3)):
                current_date += timedelta(days=random.randint(5, 15))
                update_type = random.choice(
                    ["contact details", "address", "description", "experience details"]
                )
                create_activity_log(
                    user.id,
                    ActivityLogActions.USER_PROFILE_UPDATE,
                    user.id,
                    f"Updated {update_type} for {username}",
                )

            # Simulate password changes
            if random.random() < 0.4:
                create_activity_log(
                    user.id,
                    ActivityLogActions.USER_PASSWORD_CHANGE,
                    user.id,
                    f"Password changed for {username}",
                )

            professionals.append(profile)

        db.session.commit()
        logger.info(
            f"Created {len(professionals)} professionals with comprehensive history"
        )
        return professionals

    except Exception as e:
        logger.error(f"Error creating professionals: {str(e)}")
        db.session.rollback()
        raise


def create_customers():
    customers = []
    base_date = datetime.now(timezone.utc) - timedelta(days=90)
    user = User(
        username="hamsanadam",
        email="hamsanadamdevotional@gmail.com",
        full_name=generate_valid_name(),
        phone=generate_valid_phone(),
        address=generate_valid_address(),
        pin_code=generate_valid_pincode(),
        role=USER_ROLE_CUSTOMER,
        is_active=1,
        created_at=base_date + timedelta(days=random.randint(0, 30)),
        last_login=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30)),
    )
    user.set_password("Hamsanadam@123")
    db.session.add(user)
    db.session.flush()

    profile = CustomerProfile(user_id=user.id)
    db.session.add(profile)
    db.session.flush()

    try:
        for i in range(15):  # Increased number for more variety
            username = f"customer{i + 1}"
            email = f"customer{i + 1}@email.com"
            is_active = random.random() < 0.9  # 90% chance of being active

            user = User(
                username=username,
                email=email,
                full_name=generate_valid_name(),
                phone=generate_valid_phone(),
                address=generate_valid_address(),
                pin_code=generate_valid_pincode(),
                role=USER_ROLE_CUSTOMER,
                is_active=is_active,
                created_at=base_date + timedelta(days=random.randint(0, 30)),
                last_login=datetime.now(timezone.utc)
                - timedelta(days=random.randint(0, 30)),
            )
            user.set_password(f"Customer@{i + 1}123")
            db.session.add(user)
            db.session.flush()

            # Log customer registration
            create_activity_log(
                user.id,
                ActivityLogActions.USER_REGISTER,
                user.id,
                f"Customer account created: {username}",
            )

            profile = CustomerProfile(user_id=user.id)
            customers.append(profile)
            db.session.add(profile)
            db.session.flush()

            current_date = user.created_at

            # Simulate profile updates (multiple with different fields)
            num_updates = random.randint(0, 4)
            for _ in range(num_updates):
                current_date += timedelta(days=random.randint(5, 15))
                update_type = random.choice(
                    ["phone number", "address", "email", "pin code"]
                )
                create_activity_log(
                    user.id,
                    ActivityLogActions.USER_PROFILE_UPDATE,
                    user.id,
                    f"Updated {update_type} for {username}",
                )

            # Simulate password changes (with reason)
            num_pwd_changes = random.randint(0, 2)
            for _ in range(num_pwd_changes):
                current_date += timedelta(days=random.randint(10, 30))
                reason = random.choice(
                    [
                        "routine security update",
                        "forgot previous password",
                        "security concern",
                    ]
                )
                create_activity_log(
                    user.id,
                    ActivityLogActions.USER_PASSWORD_CHANGE,
                    user.id,
                    f"Password changed for {username}: {reason}",
                )

            # Simulate login patterns
            num_logins = random.randint(3, 10)
            for _ in range(num_logins):
                current_date += timedelta(days=random.randint(1, 7))
                create_activity_log(
                    user.id,
                    ActivityLogActions.USER_LOGIN,
                    user.id,
                    f"User login from {'mobile' if random.random() < 0.7 else 'web'} device",
                )

            # Simulate account blocks/unblocks for some customers
            if random.random() < 0.2:  # 20% chance of being blocked at some point
                current_date += timedelta(days=random.randint(5, 15))
                block_reason = random.choice(
                    [
                        "Multiple invalid login attempts",
                        "Suspicious activity detected",
                        "Payment issues",
                        "Violation of terms of service",
                    ]
                )
                user.is_active = False
                create_activity_log(
                    None,  # System block
                    ActivityLogActions.CUSTOMER_BLOCK,
                    user.id,
                    f"Customer {username} blocked: {block_reason}",
                )

                # 70% chance of being unblocked later
                if random.random() < 0.7:
                    current_date += timedelta(days=random.randint(1, 7))
                    user.is_active = True
                    create_activity_log(
                        None,  # System unblock
                        ActivityLogActions.CUSTOMER_UNBLOCK,
                        user.id,
                        f"Customer {username} unblocked: Issue resolved",
                    )

            # Simulate account deletion attempts
            if (
                not is_active and random.random() < 0.3
            ):  # 30% chance for inactive accounts
                current_date += timedelta(days=random.randint(1, 5))
                reason = random.choice(
                    [
                        "Requested account closure",
                        "Moving to different location",
                        "No longer needs services",
                    ]
                )
                create_activity_log(
                    user.id,
                    ActivityLogActions.USER_DELETE,
                    user.id,
                    f"Account deletion requested: {reason}",
                )

        db.session.commit()
        logger.info(
            f"Created {len(customers)} customers with comprehensive activity history"
        )
        return customers

    except Exception as e:
        logger.error(f"Error creating customers: {str(e)}")
        db.session.rollback()
        raise


def create_services(admin_id):
    services = []
    service_data = [
        {
            "name": "AC Repair & Service",
            "price": 1500,
            "time": 120,
            "is_active": 0,
            "description": "Professional AC repair and maintenance services including gas refill, component replacement, and thorough cleaning.",
            "history": [
                ("restore", "Service restored after technician verification completed"),
                ("update", "Updated base price from 1200 to 1500"),
                ("delete", "Temporarily suspended due to lack of verified technicians"),
            ],
        },
        {
            "name": "Plumbing Service",
            "price": 800,
            "time": 60,
            "is_active": 1,
            "description": "Expert plumbing services for leak repairs, pipe installation, fixture mounting, and drainage solutions.",
            "history": [
                (
                    "update",
                    "Updated duration from 90 to 60 minutes based on service data",
                ),
                ("update", "Modified description to include drainage solutions"),
            ],
        },
        {
            "name": "Electrical Work",
            "price": 1000,
            "time": 120,
            "is_active": 1,
            "description": "Certified electrical services including wiring, installation, repairs, and safety inspections.",
            "history": [
                ("update", "Added safety inspections to service description"),
                ("delete", "Temporarily disabled for safety protocol update"),
                ("restore", "Restored after implementing new safety protocols"),
            ],
        },
        {
            "name": "Carpentry",
            "price": 1200,
            "time": 180,
            "is_active": 0,
            "description": "Professional carpentry services for furniture repair, custom woodwork, and installations.",
            "history": [
                ("update", "Increased base price from 1000 to 1200"),
                ("delete", "Service suspended for quality review"),
            ],
        },
        {
            "name": "House Painting",
            "price": 3000,
            "time": 480,
            "is_active": 1,
            "description": "Complete house painting services with premium quality paints and professional finish.",
            "history": [
                ("update", "Updated to include premium quality paints"),
                ("update", "Adjusted duration to 8 hours for accurate scheduling"),
            ],
        },
        {
            "name": "Home Cleaning",
            "price": 1000,
            "time": 240,
            "is_active": 1,
            "description": "Professional home cleaning and sanitization services.",
            "history": [
                ("update", "Added sanitization to service scope"),
                ("restore", "Restored with enhanced safety measures"),
                ("update", "Updated price to reflect new safety equipment costs"),
            ],
        },
    ]

    try:
        base_date = datetime.now(timezone.utc) - timedelta(days=90)

        for data in service_data:
            service = Service(
                name=data["name"],
                description=data["description"],
                base_price=data["price"],
                estimated_time=data["time"],  # Already in minutes
                is_active=data["is_active"],
                created_at=base_date,
            )
            services.append(service)
            db.session.add(service)
            db.session.flush()

            create_activity_log(
                admin_id,
                ActivityLogActions.SERVICE_CREATE,
                service.id,
                f"Created new service: {service.name}",
            )

            current_date = base_date
            for action_type, action_desc in data.get("history", []):
                current_date += timedelta(days=random.randint(1, 5))

                if action_type == "update":
                    create_activity_log(
                        admin_id,
                        ActivityLogActions.SERVICE_UPDATE,
                        service.id,
                        f"Updated service {service.name}: {action_desc}",
                    )
                elif action_type == "delete":
                    service.is_active = False
                    create_activity_log(
                        admin_id,
                        ActivityLogActions.SERVICE_DELETE,
                        service.id,
                        f"Deactivated service {service.name}: {action_desc}",
                    )
                elif action_type == "restore":
                    service.is_active = True
                    create_activity_log(
                        admin_id,
                        ActivityLogActions.SERVICE_RESTORE,
                        service.id,
                        f"Restored service {service.name}: {action_desc}",
                    )

        db.session.commit()
        return services

    except Exception as e:
        logger.error(f"Error creating services: {str(e)}")
        db.session.rollback()
        raise


def create_requests_and_reviews(services, professionals, customers, admin_id):
    review_templates = [
        ("Excellent service! Very professional and punctual. {}", 5, False),
        ("Great work quality and attention to detail. {}", 5, False),
        (
            "Outstanding service, highly recommended! {}",
            5,
            True,
            "Suspected fake review",
        ),
        ("Good service, met expectations. {}", 4, False),
        ("Professional and efficient work. {}", 4, False),
        ("Quality service but a bit expensive. {}", 4, False),
        ("Average service, room for improvement. {}", 3, False),
        (
            "Work done but communication was poor. {}",
            3,
            True,
            "Unprofessional behavior",
        ),
        ("Below expectations, multiple issues. {}", 2, True, "Service quality issues"),
        ("Very disappointing service. {}", 1, True, "Multiple issues reported"),
    ]

    service_request = ServiceRequest(
        service_id=1,
        customer_id=1,
        professional_id=None,
        date_of_request=datetime.now(timezone.utc),
        preferred_time=datetime.combine(
            (datetime.now(timezone.utc) + timedelta(days=1)).date(), time(16, 0)
        ),
        description="Need ",
        status="created",
        date_of_assignment=None,
        date_of_completion=None,
        remarks=None,
    )
    db.session.add(service_request)
    db.session.flush()

    try:
        base_date = datetime.now(timezone.utc) - timedelta(days=90)

        for customer in customers:
            for _ in range(random.randint(2, 5)):  # 2-5 requests per customer
                service = random.choice([s for s in services if s.is_active])
                professional = random.choice(
                    [p for p in professionals if p.user.is_active and p.is_verified]
                )

                request_date = base_date + timedelta(days=random.randint(0, 85))

                # Preferred time must be AFTER request date
                hours_after_request = random.randint(1, 8)  # 1-8 hours after request
                preferred_time = request_date + timedelta(hours=hours_after_request)

                # Ensure preferred time is within business hours (9 AM - 6 PM)
                business_start = datetime.combine(
                    preferred_time.date(), time(9, 0)
                ).replace(tzinfo=timezone.utc)
                if preferred_time.time() < time(9, 0):
                    preferred_time = business_start

                service_end_time = preferred_time + timedelta(
                    minutes=service.estimated_time
                )

                # Create a datetime object for 6 PM on the same day
                business_end_time = datetime.combine(
                    preferred_time.date(), time(18, 0)
                ).replace(tzinfo=timezone.utc)

                # If service would end after business hours
                if service_end_time > business_end_time:
                    # Move to next business day
                    next_day = preferred_time.date() + timedelta(days=1)
                    preferred_time = datetime.combine(next_day, time(9, 0)).replace(
                        tzinfo=timezone.utc
                    )

                current_time = datetime.now(timezone.utc)

                # Determine status
                if preferred_time < current_time:
                    status = REQUEST_STATUS_COMPLETED
                elif request_date < current_time and random.random() < 0.7:
                    status = REQUEST_STATUS_ASSIGNED
                else:
                    status = REQUEST_STATUS_CREATED

                # Ensure assignment happens AFTER request creation
                date_of_assignment = (
                    request_date + timedelta(hours=random.randint(1, 4))
                    if status != REQUEST_STATUS_CREATED
                    else None
                )

                # Ensure completion happens AFTER assignment
                date_of_completion = None
                if status == REQUEST_STATUS_COMPLETED and date_of_assignment:
                    service_duration = timedelta(minutes=service.estimated_time)
                    # Completion time is assignment time + service duration + random buffer
                    date_of_completion = (
                        date_of_assignment
                        + service_duration
                        + timedelta(minutes=random.randint(0, 30))
                    )

                # Create service request
                service_request = ServiceRequest(
                    service_id=service.id,
                    customer_id=customer.id,
                    professional_id=professional.id
                    if status != REQUEST_STATUS_CREATED
                    else None,
                    date_of_request=request_date,
                    preferred_time=preferred_time,
                    description=f"Need {service.name} - {fake.sentence()}",
                    status=status,
                    date_of_assignment=date_of_assignment,
                    date_of_completion=date_of_completion,
                    remarks="Service completed successfully."
                    if status == REQUEST_STATUS_COMPLETED
                    else None,
                )
                db.session.add(service_request)
                db.session.flush()

                # Log request creation
                create_activity_log(
                    customer.id,
                    ActivityLogActions.REQUEST_CREATE,
                    service_request.id,
                    f"Created service request for {service.name}",
                )

                # Handle assignment and completion
                if status != REQUEST_STATUS_CREATED:
                    create_activity_log(
                        professional.id,
                        ActivityLogActions.REQUEST_ASSIGN,
                        service_request.id,
                        "Professional accepted the service request",
                    )

                    if status == REQUEST_STATUS_COMPLETED:
                        create_activity_log(
                            professional.id,
                            ActivityLogActions.REQUEST_COMPLETE,
                            service_request.id,
                            "Service completed as scheduled",
                        )

                        # Add review (90% chance for completed services)
                        if random.random() < 0.9:
                            review_template = random.choice(review_templates)
                            review = Review(
                                service_request_id=service_request.id,
                                rating=review_template[1],
                                comment=review_template[0].format(fake.sentence()),
                                is_reported=review_template[2],
                                report_reason=review_template[3]
                                if len(review_template) > 3
                                else None,
                                created_at=date_of_completion,
                            )
                            db.session.add(review)
                            db.session.flush()

                            # Log review creation and handle reports
                            create_activity_log(
                                customer.id,
                                ActivityLogActions.REVIEW_SUBMIT,
                                review.id,
                                f"Submitted {review.rating}-star review",
                            )

                            if review.is_reported:
                                create_activity_log(
                                    professional.id,
                                    ActivityLogActions.REVIEW_REPORT,
                                    review.id,
                                    f"Review reported: {review.report_reason}",
                                )

                                # Admin review action
                                if random.random() < 0.6:
                                    create_activity_log(
                                        admin_id,
                                        ActivityLogActions.REVIEW_DISMISS,
                                        review.id,
                                        "Investigation complete - Review upheld",
                                    )
                                else:
                                    create_activity_log(
                                        admin_id,
                                        ActivityLogActions.REVIEW_REMOVE,
                                        review.id,
                                        "Review removed after investigation",
                                    )

                            # Update professional's rating
                            prof_reviews = (
                                Review.query.join(ServiceRequest)
                                .filter(
                                    ServiceRequest.professional_id == professional.id
                                )
                                .all()
                            )
                            if prof_reviews:
                                total_ratings = sum(r.rating for r in prof_reviews)
                                professional.average_rating = round(
                                    total_ratings / len(prof_reviews), 1
                                )

                # Handle cancellations (30% chance)
                if random.random() < 0.3 and status in [
                    REQUEST_STATUS_CREATED,
                    REQUEST_STATUS_ASSIGNED,
                ]:
                    service_request.status = "cancelled"
                    create_activity_log(
                        customer.id if random.random() < 0.7 else professional.id,
                        ActivityLogActions.REQUEST_CANCEL,
                        service_request.id,
                        "Request cancelled"
                        if status == REQUEST_STATUS_CREATED
                        else "Service cancelled after assignment",
                    )

        db.session.commit()

    except Exception as e:
        logger.error(f"Error creating requests and reviews: {str(e)}")
        db.session.rollback()
        raise


def clear_static_directory():
    """Clear all files from the verification documents upload directory"""
    doc_directory = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "static/uploads/verification_docs"
    )

    try:
        if os.path.exists(doc_directory):
            # Remove all files in the directory
            for filename in os.listdir(doc_directory):
                file_path = os.path.join(doc_directory, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            logger.info(f"Cleared all files from {doc_directory}")
        else:
            logger.info(f"Upload directory {doc_directory} does not exist yet")

    except Exception as e:
        logger.error(f"Error clearing static directory: {str(e)}")
        raise
