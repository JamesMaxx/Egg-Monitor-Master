# Egg Monitor Master MVP

## Overview

Egg Monitor Master is a web-based application designed for monitoring and managing egg incubators. It provides users with the ability to register accounts, log in securely, and monitor the temperature and humidity levels inside their incubators in real-time. The application also offers features such as email verification, role-based access control, and customizable settings to enhance user experience and security.

## Features

1. **User Registration and Login:**

   - Users can sign up for new accounts by providing a username, password, and email address.
   - Email verification is implemented to ensure the security of user accounts.
   - Registered users can log in securely using their username and password.

2. **Real-time Monitoring:**

   - Once logged in, users can monitor the temperature and humidity levels inside their incubators in real-time.
   - The application provides visual representations of the data using interactive line and bar charts.

3. **Customizable Settings:**

   - Users have the option to customize settings for each incubator, including temperature and humidity thresholds, sampling intervals, and notification preferences.

4. **Alerts and Notifications:**

   - Alerts and notifications are integrated to notify users of abnormal temperature or humidity levels.
   - Users can receive notifications via email or SMS when predefined thresholds are exceeded.

5. **Role-Based Access Control (RBAC):**

   - The application implements role-based access control to manage user permissions.
   - Different roles (e.g., admin, regular user) are assigned to users, and access to certain features is restricted based on their roles.

6. **Responsive Design:**

   - The application incorporates responsive design principles to ensure optimal user experience across various screen sizes and devices.

## Setup Instructions

1. Clone the repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Configure the email server settings in the `config.py` file.
4. Run the application using `python app.py`.
5. Access the application in your web browser at [http://localhost:8050](http://localhost:8050).

## Contributors

- Mwanthi Waita (<elvismwanthi@gmail.com>)
- JamesMax Munene (<jamesmaxmunene@gmail.com>)

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

- Special thanks to Flask and Dash for providing the frameworks used in this project.
- Inspiration and guidance from various open-source projects and community forums.
