![Dashboard reading of line graph](/static/Readme_image.JPG)

# E.M.M. (Egg Monitor Master) System MVP Overview

## Table of Contents


- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
  - [Client-Side (Frontend)](#client-side-frontend)
  - [Server-Side (Backend)](#server-side-backend)
  - [Database](#database)
  - [User Authentication](#user-authentication)
- [Technical Implementation](#technical-implementation)
  - [Hashing Passwords](#hashing-passwords)
  - [Database Management](#database-management)
  - [User Registration and Authentication](#user-registration-and-authentication)
- [Additional Technical Details](#additional-technical-details)
  - [Data Generation Module](#data-generation-module)
- [Challenges](#challenges)
  - [Scalability](#scalability)
  - [Real-Time Data Updates](#real-time-data-updates)
  - [Security](#security)
  - [User Experience](#user-experience)
- [Requirements and Dependencies](#requirements-and-dependencies)
- [Open to Further Research and Updates](#open-to-further-research-and-updates)
- [EMM  (EGG MONITOR MANAGEMENT) SYSTEM GitHub Repository](#github-repository)
- [Conclusion](#conclusion)
- [Contributors](#contributors)


## Introduction

Welcome to the E.M.M. System MVP README, where we introduce an innovative solution designed to revolutionize egg incubation management. In this project, we strive to provide a comprehensive platform that caters to the diverse needs of poultry farming and enthusiasts, ensuring optimal conditions for egg incubation is paramount for successful hatching and healthy chicks. The E.M.M. System addresses the challenges faced by poultry farmers and enthusiasts by providing a comprehensive platform for monitoring and managing egg incubators with precision and ease.

## Architecture Overview

[![Project's Architecture](/static/Architecture.PNG)Project's Architecture](/static/Architecture.PNG)

### Client-Side (Frontend)

- Developed using HTML, CSS, and JavaScript.
- Utilizes React components for dynamic and interactive elements.
- User authentication module ensures secure logins and sign-ups.

### Server-Side (Backend)

- Powered by Flask framework.
- API routes for communication.
- Database access layer using SQLAlchemy.
- Backend console implemented in Python for server-side operations.

### Database

- SQL database (SQLite) stores user data and incubator readings.
- Tables include 'users' and 'incubator_readings'.
- API (Application Programming Interface): Provides endpoints for user-related operations and dashboard data retrieval.
- Handles communication between the frontend and backend components.

## Data Visualization

Utilizes Dash framework for interactive data visualization.
Plotly library used to generate graphs and tables dynamically.
[![Dashboard](/static/Readme_dashborad.png)Dashboard's line graph of incubator reading](/static/Readme_dashborad.png)
<br>
<br>
[![Dashboard](/static/bargraph_readme.JPG)Dashboard's bar graph of incubator reading](/static/bargraph_readme.JPG)

<br >


# Backend Console

Python script executes background tasks and server-side operations.
Facilitates data simulation for testing purposes.

### User Authentication


The user authentication in the provided code is implemented using a combination of techniques:

#####    1: Password Hashing:
User passwords are hashed using the SHA256 algorithm with a unique salt for each user. This ensures that even if the database is compromised, the passwords cannot be easily decrypted.
#####    2: Session Management:
Flask session management is used to maintain user sessions after login. When a user successfully logs in, their username is stored in the session, allowing them to access protected routes without having to log in again for each request.
#####    3: Login Functionality:
The login function verifies the user's credentials by comparing the hashed password stored in the database with the hashed version of the password provided during login. If the two hashes match, the user is considered authenticated and their username is stored in the session.
#####    4: Registration Functionality:
The register function allows new users to create an account by storing their username and hashed password in the database. Before storing the password, it is hashed using a randomly generated salt to enhance security.
Logout Functionality: The logout function removes the user's username from the session, effectively logging them out of the system.
#####    5: Error Handling:
The code includes error handling mechanisms to deal with potential issues such as database errors or incorrect user input during registration and login.
<br>
<br> Overall, these techniques ensure that user authentication is handled securely and efficiently within the application.


# Database Management

SQLite database employed for data storage.

## Data Generation Module

Generates random temperature and humidity readings.
Associates data with a random user from the database.
Facilitates continuous data generation for testing and simulation.

# Challenges

#### Scalability

- Adapting the system to accommodate a growing number of users and incubators.
- Implementing efficient database management strategies to handle large volumes of data.

#### Real-Time Data Updates

- Ensuring timely and accurate updates of incubator readings on the dashboard.
- Optimizing API endpoints and data processing workflows for minimal latency.

#### Security

- Continuously monitoring and addressing potential security vulnerabilities.
- Enhancing user authentication mechanisms to prevent unauthorized access.

#### User Experience

- Iteratively improving the user interface for intuitive navigation and interaction.
- Gathering feedback from users to identify pain points and areas for enhancement.

# Requirements and Dependencies

To install the E.M.M. System MVP, you will need to run requirements.txt in the same directory as the project.

## Open to Further Research and Updates

We welcome collaboration and exploration to continually enhance our project. Feel free to explore our GitHub repository, contribute improvements, and engage in discussions. Together, let's drive innovation and excellence in our project.

## GitHub Repository

E.M.M. System MVP GitHub Repository: [https://github.com/JamesMaxx/Egg-Monitor-Master]

# Conclusion

The E.M.M. System MVP offers a comprehensive solution for efficient egg incubation management. With its robust architecture, advanced functionalities, and user-friendly interface, it caters to the diverse needs of poultry farmers and enthusiasts. Continuous development and refinement ensure scalability, security, and reliability for a seamless incubation experience.



## Contributors:

Mwanthi Waita
Occupation: ALX Student cohort 17 and Full-stack Software Developer
[GitHub Profile: ElvisMw](https://github.com/ElvisMw)

JamesMax Munene
Occupation: ALX Student cohort 17 and Full-stack Software Developer
[GitHub Profile: JamesMaxx](https://github.com/JamesMaxx)
<br>
<br>
<br>
Thank You!
