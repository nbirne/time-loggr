import os
import requests
import urllib.parse

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps

db = SQL("sqlite:///loggr.db")

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

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

def reformat():
    """Reformat data into a series of lists that can be passed to Chart.js (which requires lists in this format) and index.html"""
    
    # Create x_dates, a list of all dates on which time was logged (x values)
    x_dates = []
    dates = db.execute("SELECT DISTINCT DATE(timestamp) AS date FROM entries JOIN classes ON entries.class_id = classes.id WHERE entries.user_id = ? AND classes.active = 1", session["user_id"])
    for date in dates:
        x_dates.append(date["date"])

    # Create lists of classes (labels for each line on graph) 
    class_labels = []

    # Create list of minutes spent on each class at a given time (y values)
    # y_mins will be a list of lists; y_mins[i][j] = minutes logged for class i on date j
    y_mins = []

    # Populate class_labels and y_mins
    classes = db.execute("SELECT * FROM classes WHERE user_id = ? AND active = 1", session["user_id"])
    for class_row in classes:
        # Add class to class_labels
        class_labels.append(class_row["class"])
        
        # Add list to y_mins
        y_mins.append([])

        # Populate y_mins with time spent on this class on each date in x_dates
        for date in x_dates:
            # Access time value for this class on this date
            rows = db.execute("SELECT SUM(minutes) AS mins FROM entries JOIN classes ON entries.class_id = classes.id WHERE classes.id = ? AND entries.user_id = ? AND DATE(timestamp) = ?", 
                              class_row["id"], session["user_id"], date)
            
            # Append this value to list (or 0 if no time was logged for this class on this date)
            mins = rows[0]["mins"] if rows[0]["mins"] else 0
            y_mins[len(y_mins) - 1].append(mins)

    # Store total minutes over each date, for use in heatmap
    totals = []
    for i in range(len(x_dates)):
        # Initialize total to 0
        total = 0

        # Add time spent on each class on date i to total (a class_list is a list of time spent on each date for a class)
        for class_list in y_mins:
            total += class_list[i]
        
        # Append total time spent on date i to totals
        totals.append(total)
    
    # Store lists in dictionary called data
    data = {
        "x_dates": x_dates,
        "class_labels": class_labels,
        "y_mins": y_mins,
        "totals": totals
    }

    return data
