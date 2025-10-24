from App.controllers.staff import log_hours
from App.controllers.student import request_hours
from .user import create_user

from App.database import db


def initialize():
    db.drop_all()
    db.create_all()

    # Populating system with existing users

    create_user('alice', 'alicepass', 'student') #ID 1
    create_user('rob', 'robpass', 'student') #ID 2  
    create_user('carol', 'carolpass', 'student') #ID 3
    create_user('dave', 'davepass', 'student') #ID 4
    create_user('eve', 'evepass', 'student') #ID 5
    create_user('frank', 'frankpass', 'student') #ID 6
    create_user('grace', 'gracepass', 'student') #ID 7
    create_user('heidi', 'heidipass', 'student') #ID 8
    create_user('ivan', 'ivanpass', 'student') #ID 9
    create_user('judy', 'judypass', 'student') #ID 10

    create_user('sally', 'sallypass', 'staff') #ID 11
    create_user('steve', 'stevepass', 'staff') #ID 12
    create_user('john', 'johnpass', 'staff') #ID 13
    create_user('laura', 'laurapass', 'staff') #ID 14
    create_user('mike', 'mikepass', 'staff') #ID 15

   
    # Populating system with existing hour logs and accolades

    log_hours (11, 1, 10) # staff ID 11 is sally, student ID 1 is alice
    log_hours (11, 2, 15) # staff ID 11 is sally, student ID 2 is rob
    log_hours (12, 3, 20) # staff ID 12 is steve, student ID 3 is carol
    log_hours (12, 4, 12) # staff ID 12 is steve, student ID 4 is dave
    log_hours (13, 5, 18) # staff ID 13 is john, student ID 5 is eve
    log_hours (13, 6, 25) # staff ID 13 is john, student ID 6 is frank
    log_hours (14, 7, 8)  # staff ID 14 is laura, student ID 7 is grace
    log_hours (14, 8, 16) # staff ID 14 is laura, student ID 8 is heidi
    log_hours (15, 9, 22) # staff ID 15 is mike, student ID 9 is ivan 

    request_hours (1,10)
    request_hours (2,10)
    request_hours (3,10)
    request_hours (4,10)
    request_hours (5,10)
    request_hours (6,10)
    request_hours (6, 5)




   
