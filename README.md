# Household Services Application

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive platform connecting homeowners with skilled service professionals, enabling efficient management of household service requests.

## 📑 Table of Contents

- [Features](#-features)
- [Technologies](#-technologies)
- [System Requirements](#-system-requirements)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [License](#-license)

## ✨ Features

### User Management
- **Multiple User Roles**: Admin, Service Professional, and Customer
- **Authentication**: Secure JWT-based authentication
- **Professional Verification**: Document upload and admin verification process

### Service Management
- **Service Types**: Create, update, and manage various service types
- **Pricing and Scheduling**: Base pricing and time estimation for services

### Request Lifecycle
- **Service Booking**: Customers can create and manage service requests
- **Assignment**: Professionals can accept service requests
- **Completion**: Service status tracking with completion confirmation
- **Reviews & Ratings**: Rating system for completed services

### Administration
- **User Management**: Admin can verify, block, and manage users
- **Service Control**: Admin can create and manage service offerings
- **Dashboard**: Comprehensive statistics and monitoring

### Notifications & Reports
- **Email Notifications**: Automated emails for important events
- **Daily Reminders**: Professionals receive reminders for pending requests
- **Monthly Reports**: Automated monthly activity reports
- **Data Export**: CSV generation for service requests

## 🛠 Technologies

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database interactions
- **Marshmallow**: Schema validation and serialization
- **JWT**: Authentication tokens
- **Celery**: Asynchronous task processing
- **Redis**: Caching and message broker
- **Flask-Mail**: Email integration

### Frontend
- **Vue.js**: Frontend framework
- **Axios**: HTTP client
- **Bootstrap CSS**: CSS framework
- **Chart.js**: Data visualization

### Database
- **SQLite**

## 💻 System Requirements

- Python 3.11+
- Node.js 16+
- Redis server
- WSL (Windows Subsystem for Linux) for Windows users
- Git
- uv

## 🚀 Installation & Setup

### Clone the Repository

```bash
git clone https://github.com/21f1005494/household-services.git
cd household-services
```

### Backend Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

2. Install dependencies:

```bash
uv sync
```

3. Create a `.env` file in the project root with the following variables:

```
SQLALCHEMY_DATABASE_URI=sqlite:///database.sqlite3
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@householdservices.com
ADMIN_EMAIL=admin@example.com
```

### Redis Setup via WSL (Windows Users)

1. Install WSL if not already installed:

```bash
wsl --install
```

2. Install Redis on Ubuntu WSL:

```bash
# Update the package list
sudo apt update
# Install Redis server
sudo apt install redis-server
# Configure Redis to start on boot
sudo systemctl enable redis-server
```

3. Start Redis server:

```bash
sudo service redis-server start
```

4. Verify Redis is running:

```bash
redis-cli ping
# Should return PONG
```

### Redis Setup for macOS/Linux

```bash
# macOS (using Homebrew)
brew install redis
brew services start redis

# Linux
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

### Celery Setup

1. Open a new terminal window and activate your virtual environment
2. Start the Celery worker:

```bash
# From the project root directory
celery -A src.celery_app.celery worker --loglevel=info --pool=solo
```

3. Start the Celery beat scheduler (in a separate terminal):

```bash
celery -A src.celery_app.celery beat --loglevel=info
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm i
```

3. Create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:5000/api
```

## 🚀 Running the Application

1. Start the Flask backend server:

```bash
# From the project root directory with virtual environment activated
flask run
# The server will start at http://localhost:5000
```

2. Start the frontend development server:

```bash
# From the frontend directory
yarn dev
# The frontend will be available at http://localhost:3000
```

3. Ensure Redis and Celery services are running as described in the setup sections.

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api

## 📘 API Documentation

The API follows RESTful principles. Key endpoints include:

### Authentication
- `POST /api/login` - Authenticate user and get token

### User Management
- `POST /api/register/customer` - Register as customer
- `POST /api/register/professional` - Register as service professional
- `GET /api/profile` - Get current user profile
- `PUT /api/profile` - Update user profile

### Services
- `GET /api/services` - List available services
- `POST /api/services` - Create a new service (admin only)
- `PUT /api/services/{id}` - Update a service (admin only)

### Service Requests
- `POST /api/requests` - Create a service request
- `GET /api/customers/requests` - Get customer's requests
- `GET /api/professionals/requests` - Get professional's requests
- `POST /api/requests/{id}/accept` - Accept a request (professional)
- `POST /api/requests/{id}/complete` - Complete a request

### Reviews
- `POST /api/requests/{id}/review` - Submit a review
- `GET /api/professionals/reviews` - Get professional's reviews

For complete API documentation, see the YAML file in the `root` directory.

## 📁 Project Structure

```
household-services/
├── src/                # Backend source code
│   ├── app.py          # Flask application setup
│   ├── celery_app.py   # Celery configuration
│   ├── constants.py    # Application constants
│   ├── models.py       # Database models
│   ├── routes/         # API routes and controllers
│   │   ├── auth.py
│   │   ├── customer.py
│   │   ├── ...
│   ├── schemas/        # Marshmallow schemas
│   ├── utils/          # Utility functions
│   └── tasks.py        # Celery tasks
├── static/             # Static files
│   └── uploads/        # Uploaded files
├── templates/          # Email templates
│   └── emails/
├── frontend/           # Vue.js frontend
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
