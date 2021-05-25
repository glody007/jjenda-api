import pytest
from mongoengine import *
from mongoengine.connection import disconnect
from app.models.produit import Produit
from app.models.user import User

db = connect(host="mongodb://127.0.0.1:27017/test_db", alias="test")

@pytest.fixture(scope="module")
def drop_all():
    Produit.drop_collection()
    User.drop_collection()


@pytest.fixture(scope="module")
def exemple_produit_data():
    return {'prix': 10,
            'vendeur_id': "",
            'categorie': "phone",
            'description': "10GB",
            'url_photo': "",
            'url_thumbnail_photo': "",
            'longitude': 0,
            'latitude': 0}

@pytest.fixture(scope="module")
def exemple_user_data():
    return {'nom': 'root',
            'phone_number': "+2439999999",
            'email': "jjenda@jjenda.com"}
