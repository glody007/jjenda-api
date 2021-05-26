from mongoengine import *
import os

if os.getenv("FLASK_ENV") == "development":
    connect(host="mongodb://127.0.0.1:27017/dev_db")
else:
    db = connect(host=os.getenv("DB_URI"))

from .plan import *
from .produit import *
from .user import *
