from App.database import db
from datetime import datetime


class Accolade(db.Model):
    __tablename__ = 'accolades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))

    milestone = db.Column(db.Integer, nullable=False)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="accolades")

    def __repr__(self):
        return f"<Accolade {self.milestone} Hours for Student ID {self.student_id}>"

    def get_json(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'milestone': self.milestone,
            'awarded_at': self.format_awarded_time(),
            'milestone_name': self.milestone_name()
        }
    
    def format_awarded_time(self):
        if self.awarded_at:
            return self.awarded_at.strftime("%Y-%m-%d %H:%M")
        return None
    
    def milestone_name(self):
        if self.milestone == 10:
            return "Bronze"
        elif self.milestone == 20:
            return "Silver"
        elif self.milestone == 50:
            return "Gold"
        else:
            return f"{self.milestone} hours"




