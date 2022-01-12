# Incorporates starter code from Finance, CS50 Week 9

import os
from re import L

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology, reformat

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///loggr.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", apology="Must enter a username.")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", apology="Must enter a password.")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", apology="Invalid username or password.")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # If POST, check for errors in registration, then register new user
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.html", apology="Must enter a username.")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("register.html", apology="Must enter a password.")

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            return render_template("register.html", apology="Must confirm password.")

        # Ensure password and password confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", apology="Password and confirmation do not match.")
        
        # Ensure that username is not already in use
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows):
            return render_template("register.html", apology="Username already in use.")
        
        # Obtain hash for password
        hash = generate_password_hash(request.form.get("password"))

        # Register user in users table, and log them
        session["user_id"] = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hash)

        return redirect("/")
    
    # If GET, display registration form
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/", methods=["GET", "POST"])
@login_required
def log():
    """Log time"""
    
    # Store active classes
    classes = db.execute("SELECT * FROM classes WHERE user_id = ? AND active = 1", session["user_id"])

    # If POST, confirm that log is valid, and store in database if so
    if request.method == "POST":
        # Check that user inputted positive, float amount of time
        # request.form.get("input", type=int) will try to convert input to int; if not possible, will return None
        # Source: https://werkzeug.palletsprojects.com/en/2.0.x/datastructures/#werkzeug.datastructures.MultiDict.get
        h = request.form.get("hours", default=0, type=float)
        m = request.form.get("minutes", default=0, type=float)
        if ((not h and not m) or (h < 0) or (m < 0)):
            return render_template("index.html", apology="Invalid amount of time.", classes=classes)
        
        # Check that class exists
        class_rows = db.execute("SELECT * FROM classes WHERE class = ? AND user_id = ?", 
                                request.form.get("class"), session["user_id"])
        if len(class_rows) != 1:
            return render_template("index.html", apology="Please select a valid class.", classes=classes)
        
        # If all checks have passed, add log to entries table
        db.execute("INSERT INTO entries (user_id, minutes, class_id) VALUES (?, ?, ?)", 
                   session["user_id"], int(m + 60 * h), class_rows[0]["id"])

        return redirect("/")
    
    # If GET, display form to log time
    else:
        return render_template("index.html", classes=classes)


@app.route("/heatmap", methods=["GET"])
@login_required
def heatmap():
    """Show summary of logs as a heatmap"""

    # Format data in a usable way
    data = reformat()

    # Pass data to HTML template
    return render_template("heatmap.html", x_dates=data["x_dates"], y_mins=data["y_mins"], class_labels=data["class_labels"], totals=data["totals"])


@app.route("/graph", methods=["GET"])
@login_required
def graph():
    """Show graph of data"""

    data = reformat()
            
    return render_template("graph.html", x_dates=data["x_dates"], y_mins=data["y_mins"], class_labels=data["class_labels"])


@app.route("/history", methods=["GET"])
@login_required
def history():
    """Show history of logs"""
    
    # Get records of all logs
    logs = db.execute("SELECT * FROM entries JOIN classes ON entries.class_id = classes.id WHERE entries.user_id = ? AND classes.active = 1", session["user_id"])

    # Display these records in a table
    return render_template("history.html", logs=logs)


@app.route("/manage", methods=["GET", "POST"])
@login_required
def manage():
    """Show forms to manage classes"""
    
    # Store user's classes
    classes = db.execute("SELECT * FROM classes WHERE user_id = ?", session["user_id"])

    if request.method == "POST":
        # Respond if form to add class was submitted
        if 'add' in request.form:
            # Store name of class user wants to add
            class_name = request.form.get("class")

            # Check that user entered a class name
            if not (class_name):
                return render_template("manage.html", apology="Must enter a class.", classes=classes)
            
            # Check that class doesn't already exist
            class_rows = db.execute("SELECT * FROM classes WHERE class = ? AND user_id = ?", class_name, session["user_id"])
            if len(class_rows):
                return render_template("manage.html", apology="Class already exists.", classes=classes)
            
            # If checks pass, add class to classes table
            db.execute("INSERT INTO classes (class, active, user_id) VALUES (?, 1, ?)", class_name, session["user_id"])
        
        # Respond if activation/deactivation form submitted
        elif 'activate' in request.form:
            # Set all classes to inactive
            db.execute("UPDATE classes SET active = 0 WHERE user_id = ?", session["user_id"])

            # Activate classes that user has selected (only selected classes will be in request.form)
            class_rows = db.execute("SELECT class FROM classes WHERE user_id = ?", session["user_id"])
            for row in class_rows:
                if row["class"] in request.form:
                    db.execute("UPDATE classes SET active = 1 WHERE user_id = ? AND class = ?", session["user_id"], row["class"])

        return redirect("/")
    
    else:
        # Display forms to manage classes
        return render_template("manage.html", classes=classes)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)