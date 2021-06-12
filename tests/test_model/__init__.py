import pytest
from mongoengine import *
from flask import current_app
from mongoengine.connection import disconnect
from app.models.produit import Produit
from app.models.user import User
from app.models import init_db
from app import app

with app.app_context():
    app.config['TESTING'] = True
    init_db()

@pytest.fixture
def drop_all():
    Produit.drop_collection()
    User.drop_collection()

@pytest.fixture(scope="module")
def exemple_produit_data():
    return {'prix': 10,
            'vendeur_id': "",
            'categorie': "phone",
            'description': "10GB",
            'url_photo': "akiri.com",
            'url_thumbnail_photo': "akiri.com",
            'longitude': 0,
            'latitude': 0}

@pytest.fixture(scope="module")
def exemple_user_data():
    return {'nom': 'root',
            'password': 'password',
            'phone_number': "+2439999999",
            'email': "jjenda@jjenda.com"}

def insert_user(exemple_user_data):
    user = User.from_user_info(exemple_user_data)
    User.insert(user)
    return user

def user_count():
    return User.objects.count()

def insert_produit(exemple_produit_data):
    produit = Produit.product_from_dict(exemple_produit_data)
    Produit.insert(produit)
    return produit

def produit_count():
    return Produit.objects.count()
