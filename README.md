# **Influencer-Nexus**

Welcome to the Influencer-Nexus - a comprehensive web application designed to connect sponsors and influencers for seamless campaign management.

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

- python >3
- poetry
- npm

## **5. Installation**

### Step 1: Clone the Repository

```bash
git clone https://github.com/vagadeeshwar/influencer-nexus.git
cd influencer-nexus
```

### Step 2: Build the Frontend

```bash
cd frontend
npm i
npm run build
```

### Step 2: Set Up the Backend

```bash
cd ..
poetry shell
poetry install
```

## **6. Running the Application**

```bash
flask run
```

By default, the application will be accessible at `http://localhost:5000/`.

## **7. Acknowledgements**
Special thanks to the contributors, libraries, and frameworks that made this project possible.






