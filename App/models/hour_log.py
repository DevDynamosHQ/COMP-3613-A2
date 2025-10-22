from App.database import db
from datetime import datetime


class HourLog(db.Model):
    __tablename__ = 'hour_logs'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

    hours = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="requested")  # requested/confirmed/denied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    student = db.relationship("Student", backref="logs")
    staff = db.relationship("Staff", backref="created_logs")

    def __repr__(self):
        return f"<HourLog {self.id} - Student {self.student_id} - Hours {self.hours} - Status {self.status}>"

    def get_json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'staff_id': self.staff_id,
            'hours': self.hours,
            'status': self.status,
            'created_at': self.format_created_time(),
            'reviewed_at': self.format_reviewed_time()
        }
    
    def format_created_time(self):
        if self.created_at:
            return self.created_at.strftime("%Y-%m-%d %H:%M")
        return None

    def format_reviewed_time(self):
        if self.reviewed_at:
            return self.reviewed_at.strftime("%Y-%m-%d %H:%M")
        return "Not reviewed yet"

