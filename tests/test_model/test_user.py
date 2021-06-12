import pytest
from app.models.user import *
from app.models.plan import PlanType
from app.models.produit import Produit
from . import *

def test_from_user_info(exemple_user_data):
    user = User.from_user_info(exemple_user_data)
    assert user.nom == exemple_user_data['nom']
    assert user.email == exemple_user_data['email']
    assert user.type == UserType.ENREGISTRER
    assert user.phone_number ==  exemple_user_data['phone_number']

def test_insert(drop_all, exemple_user_data):
    user = User.from_user_info(exemple_user_data)
    assert User.objects.count() == 0
    User.insert(user)
    assert User.objects.count() == 1
    assert user.plan.type == PlanType.STANDARD['NOM']

def test_register_admin(drop_all, exemple_user_data):
    assert User.objects.count() == 0
    user = User.register_admin(exemple_user_data)
    assert User.objects.count() == 1
    assert user.type == UserType.ADMIN
    user = User.register_admin(exemple_user_data)
    assert User.objects.count() == 1

def test_add_article(drop_all, exemple_user_data, exemple_produit_data):
    user = User.from_user_info(exemple_user_data)
    User.insert(user)
    produit = Produit.product_from_dict(exemple_produit_data)
    assert Produit.objects.count() == 0
    user.add_article(produit)
    assert Produit.objects.count() == 1
    assert len(user.produits) == 1
    assert len(produit.vendeur_id) > 10
    assert produit.vendeur_id == str(user.id)

def test_user_encode_auth_token(exemple_user_data):
    user = User.from_user_info(exemple_user_data)
    User.insert(user)
    auth_token = user.encode_auth_token()
    assert isinstance(auth_token, bytes)

def test_user_decode_auth_token(exemple_user_data):
    user = User.from_user_info(exemple_user_data)
    User.insert(user)
    auth_token = user.encode_auth_token()
    assert isinstance(auth_token, bytes)
    assert User.decode_auth_token(auth_token) == str(user.id)
