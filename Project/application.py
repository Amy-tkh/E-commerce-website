from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///customers.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    purchases = db.execute("""
            SELECT p.purchase_date, p.price, p.picture_url, original_website_url, c.customer_name
            FROM purchases p
            JOIN customers c ON p.customer_id = c.customer_id
            LIMIT 100
            """)

    return render_template("index.html", purchases=purchases)

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return ("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return ("must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return ("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return ("must provide username")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            request.form.get("username"),
        )

        # Ensure username doesn't already exist
        if len(rows) == 1:
            return ("Username Already Exists")

        # Ensure password and confirmation are submitted and match
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return ("Password does not match confirmation")

        elif request.form.get("password") != request.form.get("confirmation"):
            return ("Password does not match confirmation")

        # Insert the new user to the database
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            request.form.get("username"),
            generate_password_hash(
                request.form.get("password"), method="pbkdf2", salt_length=16
            ),
        )

        return redirect("/register")
    else:
        return render_template("register.html")

@app.route("/create_purchase", methods=["GET", "POST"])
@login_required
def add_purchase():

    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        purchase_datestr = request.form.get("purchase_date")
        purchase_url = request.form.get("purchase_url")
        price = request.form.get("purchase_price")
        image_url = request.form.get("purchase_image")

        # Convert purchase_date string to datetime
        # I learned this from https://www.programiz.com/python-programming/datetime/strptime
        purchase_date = datetime.strptime(purchase_datestr, "%Y-%m-%dT%H:%M")

        # Ensure all required fields are filled
        if not customer_name or not purchase_date or not purchase_url or not price or not image_url:
            flash("Please fill in all the required fields")
            return redirect("/create_purchase")


        # Get customer_id based on the customer_name
        customer = db.execute("SELECT customer_id FROM customers WHERE customer_name = ?", customer_name)
        if not customer:
            flash("Customer not found")
            db.execute(
                "INSERT INTO customers (customer_name) VALUES (?)", customer_name
            )
            return redirect("/create_purchase")

        customer_id = customer[0]["customer_id"]

        # Insert the purchase data into the purchases table
        db.execute(
            "INSERT INTO purchases (customer_id, purchase_date, picture_url, original_website_url, price) VALUES (?, ?, ?, ?, ?)",
            customer_id, purchase_date, image_url, purchase_url, price
        )


        flash("Purchase added successfully!")
        return redirect("/")

    return render_template("addPurchase.html")

@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("new_password_confirmation")

        # Ensure old password was submitted
        if old_password is None:
            return flash("must provide old password")

        # Ensure new password and confirmation are submitted and match
        elif (
            new_password is None or confirmation is None or new_password != confirmation
        ):
            return flash("Password does not match confirmation")

        og_password_result = db.execute(
            "SELECT hash FROM users WHERE id = ? ", session["user_id"]
        )

        # Check if a result was obtained
        if og_password_result:
            og_password = og_password_result[0]["hash"]

        if check_password_hash(og_password, old_password):
            try:
                db.execute(
                    "UPDATE users SET hash = ? WHERE id = ?",
                    generate_password_hash(
                        new_password, method="pbkdf2", salt_length=16
                    ),
                    session["user_id"],
                )
                return redirect("/")
            except:
                return flash("Database error: Password could not be changed")

        return flash("Incorrect old password")

    return render_template("changePassword.html")

@app.route("/logout")
def logout():
    # Forget user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/customers", methods=["GET", "POST"])
@login_required
def customers_page():
    # Get the customer names from the database
    customers = db.execute("SELECT customer_name FROM customers")

    return render_template("customers.html", customers=customers)

@app.route("/purchase_history/<customer_name>")
@login_required
def purchase_history(customer_name):
    print(customer_name)
    # Get purchase information from the database
    purchase_history_data = db.execute("""
            SELECT p.purchase_date, p.price, p.picture_url, p.original_website_url, p.paid, p.purchase_id, c.customer_name
            FROM purchases p
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE c.customer_name = ?
            """, customer_name)
    print(purchase_history_data)

    return render_template("purchase_history.html", customer_name=customer_name, purchase_history=purchase_history_data)

@app.route("/delete_purchase/<int:purchase_id>", methods=["POST"])
@login_required
def delete_purchase(purchase_id):
    # Delete purchase from database
    db.execute(
        "DELETE FROM purchases WHERE purchase_id = ?", purchase_id
    )

    flash("Purchase deleted successfully!")
    return redirect("/purchase_history")
