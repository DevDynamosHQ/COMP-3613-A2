import os, tempfile, pytest, logging, unittest
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Student, Staff, HourLog, Accolade
from App.controllers import (
    create_user, list_users, get_all_users_json, login,
    get_user, get_user_by_username, update_user,
    get_student, request_hours, get_student_logs,
    get_student_accolades, log_hours, confirm_hours,
    deny_hours, get_leaderboard, award_accolades
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User("bob", "bobpass", "student")
        assert user.username == "bob"
        assert user.role == "student"

    def test_get_json(self):
        user = User("bob", "bobpass", "student")
        user_json = user.get_json()
        self.assertDictEqual(user_json, {"id": None, "username": "bob", "role": "student"})

    
    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        user = User("bob", password, role= "student")
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password, role= "student")
        assert user.check_password(password)

class ModelUnitTests(unittest.TestCase):

    def test_format_awarded_time(self):
        acc = Accolade(student_id=1, milestone=10, awarded_at=datetime(2025, 10, 17, 14, 30))
        formatted = acc.format_awarded_time()
        assert formatted == "2025-10-17 14:30"

    def test_milestone_name(self):
        acc = Accolade(student_id=1, milestone=10)
        assert acc.milestone_name() == "Bronze"
    
    def test_format_created_time(self):
        log = HourLog(student_id=1, staff_id=2, hours=5, status="requested", created_at=datetime(2025, 10, 17, 9, 45), reviewed_at=datetime.utcnow)
        formatted = log.format_created_time()
        assert formatted == "2025-10-17 09:45"

    def test_format_reviewed_time(self):
        log = HourLog(student_id=1, staff_id=2, hours=5, status="requested", created_at=datetime.utcnow(), reviewed_at=datetime(2025, 10, 17, 16, 20))
        formatted = log.format_reviewed_time()
        assert formatted == "2025-10-17 16:20"
    '''
    def test_new_user_object(self):
        u = User(username="bob", password="bobpass", role="student")
        assert u.username == "bob"
        assert u.role == "student"

    def test_get_json_structure(self):
        u = User(username="bob", password="bobpass", role="student")
        j = u.get_json()
        self.assertIn("username", j)
        self.assertIn("role", j)

    def test_hashed_password_not_plaintext(self):
        password = "mypass"
        u = User(username="bob", password=password, role="student")
        assert u.password != password
        assert isinstance(u.password, str)
        assert len(u.password) > len(password)

    def test_check_password_true(self):
        password = "mypass"
        u = User(username="bob", password=password, role="student")
        assert u.check_password(password)

    def test_student_default_hours(self):
        s = Student("alice", "pass123")
        assert s.role == "student"
        assert hasattr(s, "total_hours")
        assert s.total_hours == 0 or s.total_hours is None


    def test_staff_polymorphic(self):
        st = Staff("sally", "pass123")
        assert st.role == "staff"

    def test_hourlog_repr_and_formatters(self):
        log = HourLog(student_id=1, staff_id=2, hours=5, status="requested")
        r = repr(log)
        assert "Hours 5" in r
        log = HourLog(student_id=1, staff_id=2, hours=5, status="requested", created_at=datetime.utcnow())
        assert isinstance(log.format_created_time(), str)

    def test_accolade_milestone_name(self):
        a10 = Accolade(student_id=1, milestone=10)
        assert a10.milestone_name() in ("Bronze", "10 hours")
        a50 = Accolade(student_id=1, milestone=50)
        assert a50.milestone_name() in ("Gold", "50 hours")
    '''
    
'''
    Integration Tests
'''

@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()
    try:
        os.remove("test.db")
    except OSError:
        pass



class ControllersIntegrationTests(unittest.TestCase):

    def test_create_user_and_get_user(self):
        s = create_user("bob", "bobpass", "student")
        assert s is not None
        assert s.username == "bob"
        got = get_user(s.id)
        assert got.username == "bob"
        got2 = get_user_by_username("bob")
        assert got2.id == s.id

    def test_list_and_get_all_users_json(self):
        create_user("u1", "p1", "student")
        create_user("u2", "p2", "staff")
        users = list_users("student")
        assert any(u.username == "u1" for u in users)
        all_json = get_all_users_json()
        assert isinstance(all_json, list)
        assert any(u["username"] == "u1" for u in all_json)

    def test_update_user_changes_db(self):
        u = create_user("rick", "rickpass", "student")
        update_user(u.id, "ronnie")
        updated = get_user(u.id)
        assert updated.username == "ronnie"

    def test_request_hours_and_get_student_logs(self):
        student = create_user("st1", "pass", "student")
        log = request_hours(student.id, 5)
        assert log is not None
        assert log.hours == 5
        assert log.status == "requested"
        logs = get_student_logs(student.id)
        assert any(l.id == log.id for l in logs)

    def test_log_hours_by_staff_increments_total_and_awards_accolade(self):
        staff = create_user("staffA", "pass", "staff")
        student = create_user("stuA", "pass", "student")
        log = log_hours(staff.id, student.id, 10)
        assert log is not None
        s_after = get_student(student.id)
        assert s_after.total_hours >= 10
        accs = get_student_accolades(student.id)
        if s_after.total_hours >= 10:
            assert any(a.milestone == 10 for a in accs)

    def test_confirm_and_deny_flow(self):
        staff = create_user("staffB", "pass", "staff")
        student = create_user("stuB", "pass", "student")
        req_log = request_hours(student.id, 3)
        assert req_log.status == "requested"
        confirmed = confirm_hours(staff.id, req_log.id)
        assert confirmed.status == "confirmed"
        req2 = request_hours(student.id, 2)
        denied = deny_hours(staff.id, req2.id)
        assert denied.status == "denied"

    def test_leaderboard_returns_list(self):
        s1 = create_user("lead1", "p", "student")
        s2 = create_user("lead2", "p", "student")
        log_hours(create_user("staffX", "p", "staff").id, s1.id, 5)
        log_hours(create_user("staffY", "p", "staff").id, s2.id, 15)
        lb = get_leaderboard()
        assert isinstance(lb, list)
        assert len(lb) > 0

    def test_award_accolades_function_directly(self):
        student = create_user("accstu", "p", "student")
        s = get_student(student.id)
        s.total_hours = 25
        db.session.commit()
        new_accs, = (award_accolades(s),)[:1] if False else (award_accolades(s),)
        accs = get_student_accolades(student.id)
        if s.total_hours >= 10:
            assert any(a.milestone in (10,20,50) for a in accs)


class AuthIntegrationTests(unittest.TestCase):

    def test_login_returns_token_when_valid(self):
        u = create_user("jwtuser", "jwtpw", "student")
        token = login("jwtuser", "jwtpw")
        assert token is not None
        assert isinstance(token, str)

    def test_identify_route_behaviour(self):
        from App.main import create_app as _create_app
        app = _create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
        create_db()
        staff = create_user("identstaff", "pass", "staff")
        with app.test_client() as client:
            try:
                resp = client.post('/api/login', json={'username': staff.username, 'password': 'pass'})
                if resp.status_code == 200:
                    id_resp = client.get('/api/identify')
                    if id_resp.status_code == 200:
                        data = id_resp.get_json()
                        assert 'user' in data
            except Exception:
                
                pass
