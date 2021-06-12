from mongoengine import *
import os


def init_db():
    from flask import current_app
    if current_app.config['TESTING']:
        connect(host=current_app.config['DB_TEST_URI'])
    else:
        connect(host=current_app.config['DB_URI'])

from .plan import *
from .produit import *
from .user import *
