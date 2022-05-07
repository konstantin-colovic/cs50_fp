import os
import sys
from functools import wraps
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///restaurant.db")


@app.route("/checkout")
@login_required
def checkout():
    return render_template("checkout.html", price = db.execute("SELECT price FROM orders WHERE user_id = :id", id = session["user_id"])[0]["price"])


@app.route("/new_order")
@login_required
def new_order():
    db.execute("INSERT INTO orders (user_id, items, price) VALUES (:id, ' ', 0);", id = session["user_id"])
    return redirect("/")


@app.route("/add_item_to_order", methods=["GET", "POST"])
@login_required
def add_item_to_order():
    items = db.execute("SELECT * FROM items")
    length = len(items)
    if request.form.get("id") == None:
        return render_template("index.html", items = items, length = length)
    product = int(request.form.get("id"))
    db.execute("UPDATE orders SET price = price + (SELECT price FROM items WHERE id = :item_id), items = items || ', ' || (SELECT item FROM items WHERE id = :item_id) WHERE user_id=:user_id", user_id = session["user_id"], item_id = product)
    return render_template("index.html", items = items, length = length)

@app.route("/")
@login_required
def index():
    items = db.execute("SELECT * FROM items")
    length = len(items)
    return render_template("index.html", items = items, length = length)


@app.route("/remove_items", methods=["GET", "POST"])
@login_required
def remove_items():
    if request.method == "GET":
        return redirect("/login")
    item_name = request.form.get("name")
    if not item_name:
        return render_template("remove_items.html")
    db.execute("DELETE FROM items WHERE item = :item", item = item_name)
    return render_template("removed_items.html", name = item_name)


@app.route("/add_items", methods=["GET", "POST"])
@login_required
def add_items():
    item_name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    if not price or not description or not item_name:
        return render_template("add_items.html")
    price = float(price)
    db.execute("INSERT INTO items (item, description, price) VALUES (:item, :description, :price)", item = item_name, description = description, price = price)
    return render_template("added_items.html", name = item_name, description = description, price = price)


@app.route("/confirm", methods=["GET", "POST"])
@login_required
def confirm():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure ID was submitted
        if not request.form.get("id"):
            return apology("must provide id", 403)

        # Delete order
        db.execute("DELETE FROM orders WHERE user_id = :id", id = request.form.get("id"))

        # Redirect admin to admin page
        return redirect("/admin")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("confirm.html")


@app.route("/admin")
@login_required
def admin():
    orders = db.execute("SELECT id, name, price, items, address FROM users JOIN orders ON orders.user_id = users.id")
    length = len(orders)
    return render_template("admin.html", orders = orders, length = length)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Check if admin
        if request.form.get("username") == "admin" and request.form.get("password") == "admin":
            session["user_id"] = "1"
            return redirect("/admin")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if request.form.get("username") == "":
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure name was submitted
        elif not request.form.get("name"):
            return apology("must provide name")

        # Ensure address was submitted
        elif not request.form.get("address") :
            return apology("must provide address")

        # Ensure e-mail was submitted
        elif not request.form.get("email") :
            return apology("must provide E-mail")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username does not exist
        if len(rows) != 0 :
            return apology("Username already exists")

        # User registered so it saves him or her
        session["user_id"] = db.execute("INSERT INTO users (username, hash, name, email, address ) VALUES (:username, :hashed_pass, :name, :email, :address);", username = request.form.get("username"), hashed_pass = generate_password_hash(request.form.get("password")), name = request.form.get("name"), email = request.form.get("email"), address = request.form.get("address")  )

        # Redirects user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
