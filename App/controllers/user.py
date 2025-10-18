from App.models import User, Student, Staff
from App.database import db

def create_user(username, password, role):
    if role not in ['student', 'staff']:
        print("Invalid role! Must be 'student' or 'staff'.")
        return
        
    if User.query.filter_by(username=username).first():
        print("Username already exists!")
        return
        
    if role == 'student':
        new_user = Student(username=username, password=password)
    elif role == 'staff':
        new_user = Staff(username=username, password=password)

    db.session.add(new_user)
    db.session.commit()
    return new_user


def list_users(type):
    if type == "student":
        return Student.query.all()
    elif type == "staff":
        return Staff.query.all()
    else:
        return User.query.all()
    


def get_leaderboard():
    students = Student.query.order_by(Student.total_hours.desc()).all()
    table = []
    previous_hours = None
    rank = 0

    for student in students:
        if student.total_hours != previous_hours:
            rank += 1
            previous_hours = student.total_hours
        table.append([rank, student.username, student.total_hours])
    return table


   

def get_user_by_username(username):
    result = db.session.execute(db.select(User).filter_by(username=username))
    return result.scalar_one_or_none()

def get_user(id):
    return db.session.get(User, id)

def get_all_users():
    return db.session.scalars(db.select(User)).all()

def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        # user is already in the session; no need to re-add
        db.session.commit()
        return True
    return None
