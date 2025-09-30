# server/testing/app_testing/app_test.py
import pytest
from app import create_app, db
from models import User, Recipe


@pytest.fixture(scope="function")
def test_app():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # in-memory DB
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


class TestSignup:
    '''Signup resource in app.py'''

    def test_creates_users_at_signup(self, test_app):
        with test_app.test_client() as client:
            response = client.post('/signup', json={
                'username': 'ashketchum',
                'password': 'pikachu',
                'bio': 'I wanna be the very best...',
                'image_url': 'https://example.com/image.jpg',
            })

            assert response.status_code == 201
            with test_app.app_context():
                new_user = User.query.filter_by(username='ashketchum').first()
                assert new_user


class TestLogin:
    '''Login resource in app.py'''

    def test_logs_in_users_with_correct_credentials(self, test_app):
        with test_app.app_context():
            user = User(username='misty')
            user.password_hash = 'test'
            db.session.add(user)
            db.session.commit()

        with test_app.test_client() as client:
            response = client.post('/login', json={
                'username': 'misty',
                'password': 'test'
            })
            assert response.status_code == 200


class TestLogout:
    '''Logout resource in app.py'''

    def test_logs_out_users(self, test_app):
        with test_app.app_context():
            user = User(username='brock')
            user.password_hash = 'hash'
            db.session.add(user)
            db.session.commit()
            user_id = user.id   # capture ID before session ends

        with test_app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = user_id
            response = client.delete('/logout')
            assert response.status_code == 204



class TestRecipes:
    '''Recipes resource in app.py'''

    def test_creates_recipes_with_201(self, test_app):
        with test_app.app_context():
            user = User(username='gary')
            user.password_hash = 'hash'
            db.session.add(user)
            db.session.commit()
            user_id = user.id   # <-- capture here

        with test_app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = user_id   # <-- use stored ID
            response = client.post('/recipes', json={
                'title': 'Grilled Cheese',
                'instructions': 'Grill it',
                'minutes_to_complete': 5
            })
            assert response.status_code == 201


    def test_returns_401_if_not_logged_in(self, test_app):
        with test_app.test_client() as client:
            response = client.post('/recipes', json={
                'title': 'Rare Candy',
                'instructions': 'Blend berries really fast for a long time to create a glowing candy treat!',
                'minutes_to_complete': 1
            })
            assert response.status_code == 401
