# **Influencer-Nexus**

Welcome to the Influencer-Nexus - a comprehensive web application designed to connect sponsors and influencers for seamless campaign management. This guide will walk you through the installation process and how to get the application up and running.

## **Table of Contents**

1.  Introduction
2.  Features
3.  Project Structure
4.  Prerequisites
5.  Installation
6.  Running the Application
7.  Acknowledgements

## **1. Introduction**

Influencer-Nexus offers a unified platform for sponsors to advertise their products/services through influencers. With features such as user authentication, intuitive dashboards, and detailed campaign management, coordinating sponsorships and engagements has never been easier!

## **2. Features**

- Role-based Access Control (Admin, Sponsor, Influencer)
- Campaign and Ad Request Management
- Personalized Dashboards
- Search Functionality for Campaigns and Influencers
- Scheduled and Async Jobs (Reminders, Reports, CSV Exports)
- Performance Caching
- And many more!

## **3. Project Structure**

The project is divided into two main parts:

- **frontend**: Contains the Vue.js source code for the user interface.
- **backend**: Contains the Flask code for the server, API endpoints, and serves the static bundled Vue.js code.

## **4. Prerequisites**

Ensure you have the following installed:

- Python (version 3.7 or newer)
- pip (Python Package Installer)
- Node.js and npm (for the frontend)
- Redis

## **5. Installation**

### Step 1: Clone the Repository

```bash
git clone [repository-url]
cd [repository-folder]
```

### Step 2: Set Up the Backend
Navigate to the backend folder:

```bash
cd backend
```
**Create a Virtual Environment (Optional but Recommended)**
```bash
python -m venv venv
```

**Activate the Virtual Environment**
- On macOS and Linux:

```bash
source venv/bin/activate
```

- On Windows:
```bash
.\venv\Scripts\activate
```

**Install Required Libraries**
The `requirements.txt` file contains a list of all the necessary Python libraries that you'll need. Install them with:

```bash
pip install -r requirements.txt
```

### Step 3: Set Up the Frontend
Navigate to the frontend folder:

```bash
cd ../frontend
```

**Install Required Packages**
The `package.json` file contains a list of all the necessary Node.js packages that you'll need. Install them with:

```bash
npm install
```

**Build the Frontend**
After installing the packages, build the Vue.js project with:
```bash
npm run build
```

This will create a `dist` folder with the bundled static files that will be served by Flask.

### Step 4: Set Up Redis
Ensure Redis is running on your machine. You can start Redis with:

```bash
redis-server
```

## **6. Running the Application**
### Step 1: Start the Backend Server
Navigate back to the backend folder and run the Flask application:

```bash
cd ../backend
flask run
```

By default, the application will be accessible at `http://localhost:5000/`.

## ***7. Acknowledgements
Special thanks to the contributors, libraries, and frameworks that made this project possible.






