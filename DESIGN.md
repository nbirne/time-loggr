# Time Loggr

## RUNTHROUGH OF EACH FLASK ROUTE:

### "/login", "/register", "/logout": For these routes, I used the a similar implementation to the Finance problem set.
- Validation: The inputted information gets passed to the Flask backend for validation. In the case of login, validation ensures that the user has entered a username and password. In the case of register, validation also ensures the user entered a password confirmation, that the password and confirmation match, and that the username is not already in use. If the user has made an invalid form submission, I opted to re-render the same page, with an apology explaining why the submission could not go through. This made more sense than sending the user to a different page and making them navigate back to the form. To minimize redundancy in the HTML files, I added a Jinja condition to the layout.html template that displays an apology if one is passed via render_template.

- Sessions: Once the user has successfully logged in, their user_id is stored in their browser using sessions. This allows them to continue using the website from their browser without needing to log in every time they access the site. The logout route clears the user's session.

- SQL: I created a users table in loggr.db, with columns id, username, and hash. Rather than storing the passwords directly, which would be a security risk, it stores a hash of the password. The loggr.db database is divided into three tables: users, classes, and entries. These tables are linked relationally -- users.id maps to classes.user_id and entries.user_id, and classes.id maps to entries.class_id. I chose to separate the data in this way so that I could have one-to-many relationships (one class to many entries, one user to many classes, etc), and to make the data more manageable by breaking it into smaller pieces. Additionally, the relational nature of the database allows the program to make queries on multiple tables joined together.


### "/": This route displays a form to log time (GET) and submits that form (POST).
- Validation: User input is validated to ensure that the user entered a positive, float amount of time and that the class exists. This process is the same as described above.

- Dropdown menu: The user selects a class from a dropdown menu of their active classes (new classes must be added in /manage). I considered allowing the user to type in a class (rather than choosing from a menu), in which case if the class did not yet exist, it would be added as a new class. I decided that the dropdown menu was preferable for a few reasons. First, it improves the user experience by removing the effort of typing out the class name. Additionally, it reduces the risk of a user accidentally creating a new class due to a typo (e.g., if the user typed CS5 instead of CS50).

- SQL: If the form is successfully submitted, the user input is converted from hours and minutes to minutes, so that the time can be stored as a single value. These time values can then be used as-is later on (like in the graph), or can be converted back to hours and minutes using Jinja (like in heatmap.html).


### "/heatmap": 
- "Reformat" helper function: The /heatmap route, as well as /graph, depends on the reformat helper function. Because this code is used twice, I moved it to helpers.py rather than copying and pasting. The goal of this function is to extract the user's logs from loggr.db into a series of lists: x_dates (all the dates on which the user has logged time), class_labels (all the user's active classes), y_mins (containing a list for each class comprised of the minutes of time logged each day for that class), and totals (total minutes logged each day). This reformatted data is then used by Jinja to render the page.
    
- Jinja: In this route as well as others, I include a condition that checks that the user has inputted information, to avoid rendering an empty table/graph/etc. If the has no logged data, Jinja will not go through the work of building the table/graph, and will instead display a message urging the user to start logging time and directing them to the right page. This is more efficient than going through the entire process of rendering the page unnecessarily, and also streamlines the user experience. 

- JS color-coding: Once the page has loaded, a function in scripts.js selects all the relevant cells in the table and styles each of them in the correct color. It uses a list ("colors") containing the possible colors - colors[0] to represent less than 1 hour, colors[1] to represent less than 2, etc. Any cell above a certain threshold will have the final color in the list. Rather than hardcoding the number of colors, it reponds to the length of the colors list; so, you could change the list of colors to a list of any length without breaking the code.


### "/graph":
- Jinja and Chart.js: This route also uses the reformatted data from the "reformat" helper function. In this case, the lists get passed to a script within graph.html responsible to generating the graph using Chart.js. The graph is a multiple line graph, with a line for each class. Since Chart.js requires several lists of values (x values, y values, labels) to be passed in, the reformatted structure of the data is essential.


### "/history":
- This route selects all of the user's logs from loggr.db, and displays them in their unaltered format as a table.


### "/manage":
- This route consists of two forms that allow the user to manage their classes. One form allows the user to add a class, and the other allows them to activate/deactivate classes. Like with previous forms, inputs are validated in app.py before being inserted into loggr.db.
- The activation/deactivation process relies on the "active" column in the "classes" table, which is set to 1 for active classes and 0 for inactive classes. When the user submits this form, all of the classes are initially set to inactive. Then, the program loops over each class and checks whether it was marked as active in the form; if so, it updates the database to show that the class is active.