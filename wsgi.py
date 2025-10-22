import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate

#this is a test comment 

from App.models.user import *
from App.models.student import *
from App.models.staff import *
from App.models.hour_log import *
from App.models.accolade import *

from App.controllers.user import *
from App.controllers.student import *
from App.controllers.staff import *
from App.controllers.hour_log import *
from App.controllers.accolade import *



from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
from tabulate import tabulate

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)


# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database.")
def init():
    initialize()
    print("Database initialized!")



"""---------------- General Commands ----------------"""
# Commands that are for testing and administration purposes only

# Command to create a new student or staff account
# flask create <username> <password> <role>

@app.cli.command("create", help="Creates a new student or staff account (default: student).")
@click.argument("username", default="bob")
@click.argument("password", default="bobpass")
@click.argument("role", default="student")
def create_user_command(username, password, role):
    new_user = create_user(username, password, role)
    if new_user:
        print(f"Created new {role} {username} with ID {new_user.id}!")
    else:
        print("User creation failed!")


# Command to list all users of filter by role
# flask list
# flask list --type <role>

@app.cli.command("list", help="List all users in the system, or only those with a specific role.")
@click.option("--type", default="all", help="Roles to filter by: student, staff or all (default: all).")
def list_user_command(type):
    users = list_users(type)
    
    if not users:
        print("No users found!")
        return
    
    table = []
    for u in users:
        table.append([u.id, u.username, u.role])

    print(tabulate(table, headers=["ID", "Username", "Role"], tablefmt="grid"))
    


"""---------------- User Commands ----------------"""
# Commands that can be used by all users

#user_cli = AppGroup('user', help='Commands available to all users.') 


# Command to view the student leaderboard
# flask user leaderboard

@app.cli.command("leaderboard", help="View student leaderboard ranked by total confirmed hours logged.")
def leaderboard_command():
    leaderboard = get_leaderboard()

    if leaderboard:
        print("Student Leaderboard")
        print(tabulate(leaderboard, headers=["Rank", "Student", "Total Hours"], tablefmt="grid"))
    else:
        print("No students found!")

#app.cli.add_command(user_cli)



""" ----------------- Student Commands ----------------- """
# Commands that can be used by students only

#student_cli = AppGroup('student', help='Commands available to students only.')


# Command to request hours
# flask student request-hours <student_id> <hours>

@app.cli.command("request-hours", help="Submit a request to log volunteer hours.")
@click.argument("student_id", type=int)
@click.argument("hours", type=int)
def request_hours_command(student_id, hours):

    log = request_hours(student_id, hours)

    if log:
        print(f"Student {log.student.username} requested {log.hours} hours!")
    else:
        print("Invalid student ID or hours <= 0!")


# Command to view personal log (shows all hours requested/confirmed/denied for student)
# flask student view-log <student_id>

@app.cli.command("view-log", help="View all logged hours, including requested, confirmed, and denied requests.")
@click.argument("student_id", type=int)
def view_student_requests_command(student_id):

    logs = get_student_logs(student_id)
    if logs:
        table = []
        for log in logs:
            if log.staff:
                staff_name = log.staff.username
            else:
                staff_name = "pending"
    
            row = [log.id, log.hours, log.status, staff_name, log.format_created_time(), log.format_reviewed_time()]
            table.append(row)

        print(f"Hour Logs for {log.student.username}:")
        print(tabulate(table, headers=["Log ID", "Hours", "Status", "Confirmed By", "Requested At", "Reviewed At"], tablefmt="grid"))
    else:
        print("Invalid student ID or no logs found!")
       

# Command to view own accolades
# flask student view-accolades <student_id>

@app.cli.command("view-accolades", help="View all personal accolades earned.")
@click.argument("student_id", type=int)
def view_accolades_command(student_id):

    accolades = get_student_accolades(student_id)

    if accolades:
        table = []
        for acc in accolades:
            row = [acc.milestone_name(), acc.milestone, acc.format_awarded_time()]
            table.append(row)
        print(f"Accolades for {accolades[0].student.username}:")
        print(tabulate(table, headers=["Accolade", "Milestone", "Awarded At"], tablefmt="grid"))

    else:
        print("Invalid student ID or no accolades found!")

        
#app.cli.add_command(student_cli)



""" ----------------- Staff Commands ----------------- """
# Commands that can be used by staff only

#staff_cli = AppGroup('staff', help='Commands available to staff only.')

# Command to log hours directly for a student (no previous request made)
# flask staff log-hours <staff_id> <student_id> <hours>

@app.cli.command("log-hours", help="Log hours for a student directly.")
@click.argument("staff_id", type=int)
@click.argument("student_id", type=int)
@click.argument("hours", type=int)
def log_hours_command(staff_id, student_id, hours):

    log = log_hours(staff_id, student_id, hours)

    if log:
        print(f"{log.hours} hours has been logged for {log.student.username} by {log.staff.username}!")
    else:
        print("Invalid staff or student ID, or hours <= 0!")


# Command to view all outstanding requests from students
# flask staff view-all-requests

@app.cli.command("view-all-requests", help="View all outstanding student requests.")
def view_all_requests_command():

    logs = get_pending_logs()

    if logs:
        table = []
        for log in logs:
            student_name = log.student.username
            row = [log.id, student_name, log.hours, log.status, log.format_created_time(), log.format_reviewed_time()]
            table.append(row)

        print(tabulate(table, headers=["Log ID", "Student", "Hours", "Status", "Requested At", "Reviewed At"], tablefmt="grid"))
    
    else:
        print("No pending requests found!")
    
    

# Command to confirm hours for a student request
# flask staff confirm-hours <staff_id> <log_id>
@app.cli.command("confirm-hours", help="Confirm a student's request for hours.")
@click.argument("staff_id", type=int)
@click.argument("log_id", type=int)
def confirm_hours_command(staff_id, log_id):

    log = confirm_hours(staff_id, log_id)

    if log:
        print(f"Confirmed {log.hours} hours for {log.student.username} by {log.staff.username}!")
    else:
        print("Invalid staff id or log id!")


# Command to deny hours for a student request
# flask staff deny-hours <staff_id> <log_id>
@app.cli.command("deny-hours", help="Deny a student's request for hours.")
@click.argument("staff_id", type=int)
@click.argument("log_id", type=int)
def deny_hours_command(staff_id, log_id):

    log = deny_hours(staff_id, log_id)

    if log:
        print(f"Denied {log.hours} hours for {log.student.username} by {log.staff.username}!")
    else:
        print("Invalid staff id or log id!")


#app.cli.add_command(staff_cli)



'''
Test Commands
'''

test = AppGroup('test', help='Testing commands.') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)