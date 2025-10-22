from App.database import db
from App.models.user import User



class Student(User):
    __tablename__ = 'students'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    total_hours = db.Column(db.Integer, default=0, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }

    def __init__(self, username, password):
        super().__init__(username, password, role='student')

    def __repr__(self):
        return f"<Student {self.id} - {self.username} | Hours: {self.total_hours}>"

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username,
            'role': self.role
        }


