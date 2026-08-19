#pip install -r requirements.txt
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# run.py is inside management/ or teacher/, so go up one level to project root

from app import create_app
from app import create_app
from shared import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)  # False if deploying True
