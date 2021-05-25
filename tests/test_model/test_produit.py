import pytest
from app.models.produit import *
from . import drop_all, exemple_produit_data


def test_product_from_dict(exemple_produit_data):
    produit = Produit.product_from_dict(exemple_produit_data)
    assert produit.prix_initial  == exemple_produit_data['prix']
    assert produit.prix_actuel  == exemple_produit_data['prix']
    assert produit.categorie  == exemple_produit_data['categorie']
    assert produit.description  == exemple_produit_data['description']
    assert produit.url_photo  == exemple_produit_data['url_photo']
    assert len(produit.created_at)  > 0

def test_location_name_from_location():
    loc_name = Produit.location_name_from_location(27.4826264, -11.6642316)
    assert 'Lubumbashi' in loc_name

def test_page(drop_all, exemple_produit_data):
    produit1 = Produit.product_from_dict(exemple_produit_data)
    produit2 = Produit.product_from_dict(exemple_produit_data)
    produit1.save()
    produit2.save()
    produits = Produit.page()
    assert len(produits) == 2

def insert(drop_all, exemple_produit_data):
    assert len(Produit.objects) == 0
    produit = Produit.product_from_dict(exemple_produit_data)
    Produit.insert(produit)
    assert len(Produit.objects) == 1
