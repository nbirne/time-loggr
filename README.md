## VIDEO: https://youtu.be/mGu__CwJLmU

---

## How to run this project:

This project can be run in VSCode, either locally on your device or via code.cs50.io. Required Python packages are cs50, Flask, and Flask-Session, which were also used for the Finance problem set. To run the program, navigate to the project directory and enter "flask run" in your terminal.


## What the website does:

Time Loggr is a time management website for students. The basic goals are to help the user understand how they allocate time between classes and visualize trends over the course of a semester. Essentially, a user can log how much time they spend on each of their classes each day over the course of a semester, and Time Loggr will then generate visual representations of this information.

Aside from log in / log out / register functionality, the website has five pages:
1. Home page (Log): Log time for your classes
2. Heatmap: View your data as a heatmap
3. Graph: View your data as a graph
4. History: View a record of all logs
5. Manage Classes: Add new classes and mark classes as active (e.g., classes you're currently taking and want to see in your heatmap and graph) or inactive (e.g., classes from previous semesters)


## Using a pre-made account:

Because Time Loggr requires data before it can generate any interesting visualizations, you may want to test the website using an account with pre-loaded data. To access such an account, you can log in with the username "N" and password "123" (no quotes). Because much of this data was inserted with a SQL query, rather than organically through the website, the timestamps visible on the History page are in a slightly modified format necessary for inserting timestamps manually (for instance, "2021-11-27T21:05:33" instead of "2021-11-27 21:05:33").

