import pytest
from flask import Flask


@pytest.fixture(autouse=True)
def _flask_app_context():
    """Keep a Flask application context active for every test.

    Several tests monkeypatch SQLAlchemy model attributes (e.g.
    ``Teacher.query``) directly. Flask-SQLAlchemy's ``query`` descriptor
    needs a live application context just to be read (even before any
    query actually runs), so without this the monkeypatching itself
    raises "Working outside of application context" long before the
    test gets to exercise any real behavior.
    """
    app = Flask(__name__)
    with app.app_context():
        yield
