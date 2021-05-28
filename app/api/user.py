from flask import request
from flask_restplus import Resource, abort, fields
from . import api_rest
from ..models import  User as UserModel
from .validation import *
from .security import require_auth, AuthType
from .resource_type import ResourceType

user_fields  = api_rest.model('User info', {
    'id': fields.String(attribute=lambda x: str(x.id)),
    'nom': fields.String(required=True, min_length=3, max_length=50),
    'phone_number': fields.String(required=True, min_length=10, max_length=13),
    'email': fields.String(required=True),
    'longitude': fields.Float(),
    'latitude': fields.Float(),
    'plan_type': fields.String(attribute=lambda x: None if x.plan == None else x.plan.type)
})

user_list_fields = api_rest.model('UserList', {
    'users': fields.List(fields.Nested(user_fields))
})

@api_rest.route('/users')
class UserList(Resource):
    @api_rest.marshal_with(user_list_fields)
    @api_rest.response(200, 'Success', user_list_fields)
    def get(self):
        return {'users' : UserModel.objects()}, 200

    @api_rest.doc(security='apiKey')
    @require_auth(type=AuthType.ADMIN)
    @api_rest.response(401, 'Unauthorized')
    @api_rest.expect(user_fields, validate=True)
    @api_rest.response(201, 'Success')
    @api_rest.response(400, 'Validation Error')
    def post(self):
        try:
            user = UserModel.from_user_info(request.json)
            UserModel.insert(user)
            return {'result': 'success', 'user': {
                'id': str(user.id),
                'nom': user.nom,
                'phone_number': user.phone_number,
                'email': user.email
            }}, 201
        except:
            return error_email_and_phone_number, 400

@api_rest.route('/user/<user_id>')
class User(Resource):
    @api_rest.marshal_with(user_fields)
    @api_rest.response(200, 'Success', user_fields)
    @api_rest.response(404, 'Ressource not found')
    @validate_ObjectId_or_404('user_id')
    def get(self, user_id):
        user = UserModel.objects.with_id(user_id)
        if user == None:
            abort(404)
        return user, 200

    @api_rest.doc(security='apiKey')
    @require_auth(res_type=ResourceType.USER, id_name='user_id')
    @api_rest.response(401, 'Unauthorized')
    @api_rest.expect(user_fields, validate=True)
    @api_rest.response(201, 'Success')
    @api_rest.response(400, 'Validation Error')
    @api_rest.response(404, 'Ressource not found')
    @validate_ObjectId_or_404('user_id')
    def put(self, user_id):
        user = UserModel.objects.with_id(user_id)
        if user == None:
            abort(404)
        try:
            user.update_from_info(request.json)
        except:
            return error_email_and_phone_number, 400
        return {'result': 'success'}, 201

    @api_rest.doc(security='apiKey')
    @require_auth(res_type=ResourceType.USER, id_name='user_id')
    @api_rest.response(401, 'Unauthorized')
    @api_rest.response(201, 'Success')
    @api_rest.response(404, 'Ressource not found')
    @validate_ObjectId_or_404('user_id')
    def delete(self, user_id):
        user = UserModel.objects.with_id(user_id)
        if user == None:
            abort(404)
        user.delete()
        return {'result': 'success'}, 200
