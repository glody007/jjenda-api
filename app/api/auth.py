from flask import request
from flask_restplus import Resource, abort, fields
from . import api_rest
from ..models import  User as UserModel
from .validation import *

user_registration_info_fields  = api_rest.model('User registration info', {
    'nom': fields.String(required=True, min_length=3, max_length=50),
    'phone_number': fields.String(required=True, min_length=10, max_length=13),
    'email': fields.String(required=True),
    'password': fields.String(required=True, min_length=3),
    'longitude': fields.Float(),
    'latitude': fields.Float()
})

user_login_info_fields  = api_rest.model('User login info', {
    'password': fields.String(required=True, min_length=3, max_length=50),
    'email': fields.String(required=True)
})

@api_rest.route('/auth/register')
class Registration(Resource):
    @api_rest.expect(user_registration_info_fields, validate=True)
    @api_rest.response(201, 'Success')
    @api_rest.response(202, 'Fail. user with same email or phone number already exist')
    @api_rest.response(400, 'Validation Error')
    def post(self):
        user_with_email = UserModel.objects(email=request.json['email']).first()
        if user_with_email != None:
            return error_user_with_same_email

        user_with_phone_number = UserModel.objects(phone_number=request.json['phone_number']).first()
        if user_with_phone_number != None:
            return error_user_with_same_phone_number
        user = UserModel.register(request.json)
        try:
            user = UserModel.register(request.json)
            auth_token = user.encode_auth_token()
        except:
            return error_email_and_phone_number
        return {'result': 'success', 'auth_token': auth_token.decode()}, 201

@api_rest.route('/auth/login')
class Login(Resource):
    @api_rest.expect(user_login_info_fields, validate=True)
    @api_rest.response(201, 'Success')
    @api_rest.response(400, 'Validation Error')
    @api_rest.response(404, 'Wrong credentials')
    def post(self):
        user = UserModel.objects(email=request.json['email']).first()
        if user == None:
            return error_wrong_credentials
        if not user.check_password(request.json['password']):
            return error_wrong_credentials
        try:
            auth_token = user.encode_auth_token()
        except:
            return error_wrong_credentials
        return {'result': 'success', 'auth_token': auth_token.decode()}, 201
