# TKH Purchase Tracker

#### Video Link
https://youtu.be/Ljh5mgpYe6g

#### Description
The TKH Purchase Tracker is a Flask web application designed for the management of online purchases for our family business. As we buy items online for our customers and ship them, this tool helps us keep track of who bought what, the corresponding costs, the source of purchase, and the image for each item.

## Features
- User authentication (register, log in, log out)
- Adding and viewing purchases
- Managing customer information
- Changing user password
- Deleting purchases

## Project Structure

### app.py
The main application file that houses the Flask application, route definitions, and configuration settings. It includes functions for user authentication, adding purchases, managing customers, and other essential features.

### layout.html
The base HTML layout template shared across different pages. It includes the navigation bar, flash message display, and the overall structure for consistent styling.

### templates/
This directory contains HTML templates for various pages, such as login, registration, purchase history, customer management, and the main dashboard. These templates use Jinja2 templating to dynamically generate content.

- **`index.html`**: The main dashboard displaying a table of recent purchases.
- **`login.html`**: The login page for user authentication.
- **`register.html`**: The registration page for creating a new user account.
- **`addPurchase.html`**: Form for adding new purchases, including customer name, purchase date, image URL, purchase URL, and price.
- **`changePassword.html`**: Form for changing the user password.
- **`customers.html`**: Page for managing and displaying a list of customers.
- **`purchase_history.html`**: Displays the purchase history for the specific customer.


### static/
Holds static assets like images and CSS files, The logo and styles.css.

### customers.db
SQLite database file storing user information, customer details, and purchase records.

## Design Choices
- **Flask**: Chose flask for its simplicity and flexibility. Flask is easy to use and I was already familiar with it.

- **SQLite Database**: Opted for SQLite due to being more familiar with it's usage. It simplifies usage and eliminates the need for a separate database server.

- **Bootstrap**: Used Bootstrap for styling to achieve a clean and responsive design. This choice speeds up the development of a visually appealing user interface.

- **Password Hashing**: Implemented secure password hashing using Werkzeug to enhance user account security.
