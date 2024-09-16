import logging
from faker import Faker
from datetime import timedelta
from . import db  # Import the shared db instance
from src.models import User, Sponsor, Influencer, Campaign, AdRequest, AdRequestStatus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()


def setup_database():
    """
    Drops all tables, recreates them, and populates the database with dummy data.
    """
    # Drop all tables
    db.drop_all()
    logger.info("Dropped all tables.")

    # Create all tables
    db.create_all()
    logger.info("Created all tables.")

    # Insert dummy data into the database
    create_dummy_data()
    logger.info("Populated database with dummy data.")


def create_dummy_data():
    users = create_dummy_users()
    sponsors = create_dummy_sponsors(users)
    influencers = create_dummy_influencers(users)
    campaigns = create_dummy_campaigns(sponsors)
    create_dummy_ad_requests(campaigns, influencers)


def create_dummy_users():
    users = []
    for _ in range(20):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            role=fake.random_element(elements=("admin", "sponsor", "influencer")),
        )
        user.set_password("password123")
        users.append(user)
        db.session.add(user)
    db.session.commit()
    logger.info("20 dummy users created.")
    return users


def create_dummy_sponsors(users):
    sponsors = []
    sponsor_users = [user for user in users if user.role == "sponsor"]
    for user in sponsor_users:
        sponsor = Sponsor(
            id=user.id,  # Ensure the Sponsor's ID matches the User's ID
            company_name=fake.company(),
            industry=fake.bs(),
            budget=fake.random_number(digits=5),
        )
        sponsors.append(sponsor)
        db.session.add(sponsor)
    db.session.commit()
    logger.info(f"{len(sponsors)} dummy sponsors created.")
    return sponsors


def create_dummy_influencers(users):
    influencers = []
    influencer_users = [user for user in users if user.role == "influencer"]
    for user in influencer_users:
        influencer = Influencer(
            id=user.id,  # Ensure the Influencer's ID matches the User's ID
            name=fake.name(),
            category=fake.random_element(
                elements=("Tech", "Lifestyle", "Fashion", "Gaming")
            ),
            niche=fake.random_element(
                elements=("Gadgets", "Travel", "Clothing", "Esports")
            ),
            reach=fake.random_number(digits=6),
        )
        influencers.append(influencer)
        db.session.add(influencer)
    db.session.commit()
    logger.info(f"{len(influencers)} dummy influencers created.")
    return influencers


def create_dummy_campaigns(sponsors):
    campaigns = []
    for sponsor in sponsors:
        for _ in range(4):  # 4 campaigns per sponsor
            start_date = fake.date_this_year()
            campaign = Campaign(
                name=fake.catch_phrase(),
                description=fake.text(),
                start_date=start_date,
                end_date=start_date + timedelta(days=fake.random_int(min=1, max=30)),
                budget=fake.random_number(digits=5),
                visibility=fake.random_element(elements=("public", "private")),
                goals=fake.sentence(),
                sponsor_id=sponsor.id,
            )
            campaigns.append(campaign)
            db.session.add(campaign)
    db.session.commit()
    logger.info(f"{len(campaigns)} dummy campaigns created.")
    return campaigns


def create_dummy_ad_requests(campaigns, influencers):
    ad_requests = []
    for campaign in campaigns:
        for _ in range(2):  # 2 ad requests per campaign
            influencer = fake.random_element(elements=influencers)
            ad_request = AdRequest(
                campaign_id=campaign.id,
                influencer_id=influencer.id,
                messages=fake.text(),
                requirements=fake.sentence(),
                payment_amount=fake.random_number(digits=4),
                status=fake.random_element(
                    elements=[
                        AdRequestStatus.PENDING,
                        AdRequestStatus.ACCEPTED,
                        AdRequestStatus.REJECTED,
                    ]
                ),
            )
            ad_requests.append(ad_request)
            db.session.add(ad_request)
    db.session.commit()
    logger.info(f"{len(ad_requests)} dummy ad requests created.")
    return ad_requests
