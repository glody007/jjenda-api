from . import *
from copy import deepcopy

def test_produit_list_get(drop_all, client, exemple_produit_data):
    resp = client.get('/api/produits')
    assert len(resp.json['produits']) == 0
    assert resp.status_code == 200
    insert_produit(exemple_produit_data)
    resp = client.get('/api/produits')
    assert len(resp.json['produits']) == 1

def test_produit_list_post(drop_all, client, exemple_produit_data):
    resp_get = client.get('/api/produits')
    assert len(resp_get.json['produits']) == 0
    resp_post = client.post('/api/produits', json=exemple_produit_data)
    assert resp_post.status_code == 201
    resp_get = client.get('/api/produits')
    assert len(resp_get.json['produits']) == 1
    exemple = deepcopy(exemple_produit_data)
    exemple['categorie'] = ''
    resp_post = client.post('/api/produits', json=exemple)
    assert resp_post.status_code == 400
    exemple = deepcopy(exemple_produit_data)
    exemple['description'] = ''
    resp_post = client.post('/api/produits', json=exemple)
    assert resp_post.status_code == 400
    exemple = deepcopy(exemple_produit_data)
    exemple['url_photo'] = ''
    resp_post = client.post('/api/produits', json=exemple)
    assert resp_post.status_code == 400
    exemple = deepcopy(exemple_produit_data)
    exemple['url_thumbnail_photo'] = ''
    resp_post = client.post('/api/produits', json=exemple)
    assert resp_post.status_code == 400

def test_produit_get(drop_all, client, exemple_produit_data):
    produit = insert_produit(exemple_produit_data)
    resp_get = client.get('/api/produit/55153a8014829a865bbf700d')
    assert resp_get.status_code == 404
    resp_get = client.get('/api/produit/{}'.format(str(produit.id)))
    assert resp_get.status_code == 200
    assert resp_get.json['categorie'] == exemple_produit_data['categorie']

def test_produit_delete(drop_all, client, exemple_produit_data):
    produit = insert_produit(exemple_produit_data)
    resp_get = client.delete('/api/produit/55153a8014829a865bbf700d')
    assert resp_get.status_code == 404
    assert produit_count() == 1
    resp_get = client.delete('/api/produit/{}'.format(str(produit.id)))
    assert resp_get.status_code == 200
    assert produit_count() == 0

def test_produit_list_post(drop_all, client, exemple_produit_data):
    produit = insert_produit(exemple_produit_data)
    resp_put = client.put('/api/produit/55153a8014829a865bbf700d', json=exemple_produit_data)
    assert resp_put.status_code == 404
    exemple = deepcopy(exemple_produit_data)
    exemple['categorie'] = ''
    resp_put = client.put('/api/produit/{}'.format(str(produit.id)), json=exemple_produit_data)
    assert resp_put.status_code ==201
    exemple = deepcopy(exemple_produit_data)
    exemple['description'] = ''
    resp_put = client.put('/api/produit/{}'.format(str(produit.id)), json=exemple)
    assert resp_put.status_code == 400
    exemple = deepcopy(exemple_produit_data)
    exemple['url_photo'] = ''
    resp_put = client.put('/api/produit/{}'.format(str(produit.id)), json=exemple)
    assert resp_put.status_code == 400
    exemple = deepcopy(exemple_produit_data)
    exemple['url_thumbnail_photo'] = ''
    resp_put = client.put('/api/produit/{}'.format(str(produit.id)), json=exemple)
    assert resp_put.status_code == 400
