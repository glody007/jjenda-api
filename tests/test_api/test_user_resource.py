from . import *

def test_user_list_get(drop_all, client, exemple_user_data):
    resp = client.get('/api/users')
    assert len(resp.json['users']) == 0
    assert resp.status_code == 200
    insert_user(exemple_user_data)
    resp = client.get('/api/users')
    assert len(resp.json['users']) == 1

def test_user_list_post(drop_all, client, exemple_user_data):
    resp_get = client.get('/api/users')
    assert len(resp_get.json['users']) == 0

    resp_post = client.post('/api/users', json=exemple_user_data)
    assert resp_post.status_code == 401

    resp_get = client.get('/api/users')
    assert len(resp_get.json['users']) == 0

    resp = client.post('/api/auth/register', json=exemple_user_data)
    token_header = {'X-API-KEY': resp.json['auth_token']}

    resp_get = client.get('/api/users')
    assert len(resp_get.json['users']) == 1

    resp_post = client.post('/api/users', json=exemple_user_data, headers=token_header)
    assert resp_post.status_code == 401

    user = insert_user(exemple_user_data)
    user.set_admin()
    admin_token = auth_token = user.encode_auth_token()
    token_header = {'X-API-KEY': admin_token}

    resp_post = client.post('/api/users', json={'nom':'root', 'phone_number':'9999966666', 'email':'rot@root.com'}, headers=token_header)
    assert resp_post.status_code == 201

    resp_get = client.get('/api/users')
    assert len(resp_get.json['users']) == 3

    resp_post = client.post('/api/users', json={'nom':'root'})
    assert resp_post.status_code == 400

    resp_post = client.post('/api/users', json={'nom':'root', 'phone_number':'099999999', 'email':'root@root'})
    assert resp_post.status_code == 400

    resp_post = client.post('/api/users', json={'nom':'root', 'phone_number':'099', 'email':'root@root.com'})
    assert resp_post.status_code == 400

def test_user_get(drop_all, client, exemple_user_data):
    user = insert_user(exemple_user_data)
    resp_get = client.get('/api/user/55153a8014829a865bbf700d')
    assert resp_get.status_code == 404
    resp_get = client.get('/api/user/23')
    assert resp_get.status_code == 404
    resp_get = client.get('/api/user/{}'.format(str(user.id)))
    assert resp_get.status_code == 200
    assert resp_get.json['nom'] == exemple_user_data['nom']

def test_user_delete(drop_all, client, exemple_user_data):
    user = insert_user(exemple_user_data)
    auth_token =  user.encode_auth_token()
    token_header = {'X-API-KEY': auth_token}

    resp_del = client.delete('/api/user/55153a8014829a865bbf700d', headers=token_header)
    assert resp_del.status_code == 401
    resp_del = client.delete('/api/user/23', headers=token_header)
    assert resp_del.status_code == 404
    assert user_count() == 1
    resp_del = client.delete('/api/user/{}'.format(str(user.id)), headers=token_header)
    assert resp_del.status_code == 200
    assert user_count() == 0

def test_user_put(drop_all, client, exemple_user_data):
    user = insert_user(exemple_user_data)
    auth_token =  user.encode_auth_token()
    token_header = {'X-API-KEY': auth_token}

    resp_put = client.put('/api/user/55153a8014829a865bbf700d', json=exemple_user_data, headers=token_header)
    assert resp_put.status_code == 401
    resp_get = client.put('/api/user/23', json=exemple_user_data, headers=token_header)
    assert resp_get.status_code == 404
    resp_put = client.put('/api/user/{}'.format(str(user.id)), json=exemple_user_data, headers=token_header)
    assert resp_put.status_code == 201
    resp_put= client.put('/api/user/{}'.format(str(user.id)), json={'nom':'root'})
    assert resp_put.status_code == 400
    resp_put = client.put('/api/user/{}'.format(str(user.id)), json={'nom':'root', 'phone_number':'099999999', 'email':'root@root'})
    assert resp_put.status_code == 400
    resp_put = client.put('/api/user/{}'.format(str(user.id)), json={'nom':'root', 'phone_number':'099', 'email':'root@root.com'})
    assert resp_put.status_code == 400
