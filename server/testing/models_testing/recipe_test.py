import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe


class TestRecipe:
    '''Recipe in models.py'''

    def setup_method(self):
        """Run before each test."""
        with app.app_context():
            db.create_all()       # ensure tables exist
            Recipe.query.delete()
            db.session.commit()

    def teardown_method(self):
        """Run after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        with app.app_context():
            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In"""
                + """ raptures building an bringing be. Elderly is detract"""
                + """ tedious assured private so to visited. Do travelling"""
                + """ companions contrasted it. Mistress strongly remember"""
                + """ up to. Ham him compass you proceed calling detract."""
                + """ Better of always missed we person mr. September"""
                + """ smallness northward situation few her certainty"""
                + """ something.""",
                minutes_to_complete=60,
            )
            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.minutes_to_complete == 60

    def test_requires_title(self):
        '''requires each record to have a title.'''
        with app.app_context():
            recipe = Recipe()
            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''must raise either an IntegrityError or a custom validation ValueError'''
        with app.app_context():
            with pytest.raises((IntegrityError, ValueError)):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="idk lol",  # < 50 chars
                )
                db.session.add(recipe)
                db.session.commit()
