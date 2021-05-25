from flask import request
from flask_restplus import Resource, abort
from . import api_rest
from ..models.user import  User as UserModel

@api_rest.route('/users')
class UserList(Resource):
    """ Unsecure Resource Class: Inherit from Resource """

    def get(self):
        return UserModel.objects().to_json()

    def post(self):
        UserModel.from_user_info({
            'nom':'root',
            'email':'glodymbutwile@gmail.com',
            'phone_number':'+2439999999'
        })
        return {'result': 'success'}, 201

@api_rest.route('/user/<user_id>')
class User(Resource):
    """ Unsecure Resource Class: Inherit from Resource """
    def get(self, user_id):
        user = UserModel.objects(unique_id=str(user_id)).first()
        if user == None:
            abort(404)
        return user.to_json()

    def put(self, user_id):
        json_payload = request.json
        return {'name': json_payload}, 201
