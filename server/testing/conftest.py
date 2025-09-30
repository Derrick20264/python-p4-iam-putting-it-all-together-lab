import pytest
from app import create_app
from models import db, User, Recipe  # import models so tables register

@pytest.fixture(scope="module")
def test_app():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()     # now tables for User + Recipe are created
        yield app
        db.session.remove()
        db.drop_all()
