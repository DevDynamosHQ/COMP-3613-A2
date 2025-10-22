from App.database import db
from App.models.user import User



class Staff(User):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'staff'
    }

    def __init__(self, username, password):
        super().__init__(username, password, role='staff')

    def __repr__(self):
        return f"<Staff {self.id} - {self.username}>"

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username,
            'role': self.role
        }






