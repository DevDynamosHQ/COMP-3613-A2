from App.models import Student
from App.database import db
from App.models.hour_log import HourLog


def request_hours(student_id, hours):
    student = get_student(student_id)

    if student and hours > 0:
        log = HourLog(hours=hours, student=student, status ="requested")
        db.session.add(log)
        db.session.commit()
        return log
    return None


def get_student_logs(student_id):
    student = get_student(student_id)
    if student:
        return student.logs
    return None


def get_student_accolades(student_id):
    student = get_student(student_id)
    if student:
        milestones = [10, 20, 50]
        result = []
        for m in milestones:
            for accolade in student.accolades:
                if accolade.milestone == m:
                    result.append(accolade)
        return result
    return None




def get_student(student_id):
    return Student.query.get(student_id)