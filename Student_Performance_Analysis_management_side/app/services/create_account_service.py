import re
import bcrypt as bp

from app.models.Administration import Admin
from app.extensions import db

def create_account(user,password,confirm_password,Table):
   pattern = r"^(?=.*[0-9])(?=.*[a-z]).+$"
   if password==confirm_password and re.match(pattern,password):
      new_admin=Table(Gmail=user,password=bp.hashpw(password.encode(),bp.gensalt()))
      try:
         db.session.add(new_admin)
         db.session.commit()
      except Exception as e:
         print(f'ERROR:{e}')
         return ""
      return True
   else:
        return "pass"