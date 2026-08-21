#pip install -r requirements.txt
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# run.py is inside management/ or teacher/, so go up one level to project root
from sqlalchemy.exc import ProgrammingError

from app import create_app
from shared import db

try:
   app = create_app()

   if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True,port=8000)  # False if deploying True
except ProgrammingError as e:
   from create_databases import create_database
   create_database()
   print("Due to Database ERROR created DATABASE so run again.")
except Exception as e:
   print(f'ERROR:{e}')
