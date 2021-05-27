from . import *
from copy import deepcopy

def test_auth_register(drop_all, client, exemple_user_data):
    resp = client.post('/api/auth/register', json={'nom':'root'})
    assert resp.status_code == 400

    resp = client.post('/api/auth/register', json={'nom':'root', 'phone_number':'099999999', 'email':'root@root'})
    assert resp.status_code == 400

    resp = client.post('/api/auth/register', json={'nom':'root', 'phone_number':'099', 'email':'root@root.com'})
    assert resp.status_code == 400

    resp = client.post('/api/auth/register', json=exemple_user_data)
    assert resp.status_code == 201
    assert len(resp.json['auth_token']) > 30

    exemple_with_same_mail = deepcopy(exemple_user_data)
    exemple_with_same_mail['phone_number'] = "0997028901"
    resp = client.post('/api/auth/register', json=exemple_with_same_mail)
    assert resp.status_code == 202
    assert 'Email' in resp.json['message']

    exemple_with_same_phone_number = deepcopy(exemple_user_data)
    exemple_with_same_phone_number['email'] = "akiri@akiri.com"
    resp = client.post('/api/auth/register', json=exemple_with_same_phone_number)
    assert resp.status_code == 202
    assert 'Phone' in resp.json['message']

def test_auth_login(drop_all, client, exemple_user_data):
    resp = client.post('/api/auth/login', json=exemple_user_data)
    assert resp.status_code == 404
    assert 'Wrong credentials' in resp.json['message']

    resp = client.post('/api/auth/register', json=exemple_user_data)
    assert resp.status_code == 201

    resp = client.post('/api/auth/login', json=exemple_user_data)
    assert resp.status_code == 201
    assert len(resp.json['auth_token']) > 30
