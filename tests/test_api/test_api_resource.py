""" pytests for Flask """

import pytest
from app import app
from . import client

def test_api(client):
    resp = client.get('/api/')
    assert resp.status_code == 200


'''def test_secure_resource_pass(client):
    resp = client.get('/api/secure-resource/two',
                      headers={'authorization': 'Bearer x'})
    assert resp.status_code == 200'''
