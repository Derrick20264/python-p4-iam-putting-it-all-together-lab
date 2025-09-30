# app.py
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = b"super-secret-key"
    app.json.compact = False

    db.init_app(app)
    migrate.init_app(app, db)

    # create a fresh Api for every app
    api = Api(app)

    from models import User, Recipe

    # -------- Resources --------
    class Signup(Resource):
        def post(self):
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            bio = data.get("bio", "")
            image_url = data.get("image_url", "")

            if not username or not password:
                return {"error": "Username and password required"}, 400

            try:
                user = User(
                    username=username,
                    bio=bio,
                    image_url=image_url,
                )
                user.password_hash = password  
                db.session.add(user)
                db.session.commit()
                session["user_id"] = user.id
                return user.to_dict(), 201
            except IntegrityError:
                db.session.rollback()
                return {"error": "Username already exists"}, 400

    class CheckSession(Resource):
        def get(self):
            user_id = session.get("user_id")
            if not user_id:
                return {"message": "401: Not Authorized"}, 401
            user = User.query.get(user_id)
            if not user:
                return {"message": "401: Not Authorized"}, 401
            return user.to_dict(), 200

    class Login(Resource):
        def post(self):
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            user = User.query.filter_by(username=username).first()
            if user and user.authenticate(password):
                session["user_id"] = user.id
                return user.to_dict(), 200
            return {"error": "Invalid credentials"}, 401

    class Logout(Resource):
        def delete(self):
            if "user_id" not in session:
                return {"message": "401: Not Authorized"}, 401
            session.pop("user_id", None)
            return {}, 204

    class RecipeIndex(Resource):
     def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"message": "401: Not Authorized"}, 401

        data = request.get_json()
        instructions = data.get("instructions")

        if not instructions:
            return {"errors": ["Instructions required"]}, 422

        recipe = Recipe(
            title=data.get("title"),
            instructions=instructions,
            minutes_to_complete=data.get("minutes_to_complete"),
            user_id=user_id,
        )
        db.session.add(recipe)
        db.session.commit()
        return recipe.to_dict(), 201


    # Register endpoints
    api.add_resource(Signup, "/signup")
    api.add_resource(Login, "/login")
    api.add_resource(Logout, "/logout")
    api.add_resource(CheckSession, "/check_session")
    api.add_resource(RecipeIndex, "/recipes")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
