from flask import request
from flask_restplus import Resource, abort, fields
from . import api_rest
from .resource_type import ResourceType
from ..models import Produit as ProduitModel
from ..models import User as UserModel
from .validation import *
from .security import require_auth


produit_basic_fields  = api_rest.model('Produit basic', {
    'categorie': fields.String(required=True, min_length=3),
    'prix': fields.Integer(required=True),
    'description': fields.String(required=True, min_length=3),
    'url_photo': fields.String(required=True, min_length=5),
    'url_thumbnail_photo': fields.String(required=True, min_length=5),
    'longitude': fields.Float(),
    'latitude': fields.Float()
})

produit_complete_fields = api_rest.model('Produit complete', {
    'id': fields.String(required=True, attribute=lambda x: str(x.id)),
    'categorie': fields.String(required=True),
    'prix': fields.Integer(required=True),
    'description': fields.String(required=True),
    'url_photo': fields.String(required=True),
    'url_thumbnail_photo': fields.String(required=True),
    'longitude': fields.Float(),
    'latitude': fields.Float(),
    'created_at': fields.String(required=True),
    'location_name': fields.String()
})

produit_list_fields = api_rest.model('ProduitList', {
    'produits': fields.List(fields.Nested(produit_complete_fields))
})

response_post_produit_fields = api_rest.model('Response post produit success', {
    'result': fields.String(required=True),
    'produit': fields.Nested(produit_complete_fields)
})

@api_rest.route('/produits')
class ProduitList(Resource):
    @api_rest.marshal_with(produit_list_fields)
    @api_rest.response(200, 'Success', produit_list_fields)
    def get(self):
        return {'produits' : ProduitModel.objects()}, 200

    @api_rest.marshal_with(response_post_produit_fields)
    @api_rest.doc(security='apiKey')
    @require_auth()
    @api_rest.response(401, 'Unauthorized')
    @api_rest.expect(produit_basic_fields, validate=True)
    @api_rest.response(201, 'Success')
    @api_rest.response(400, 'Validation Error')
    def post(self):
        user_id = UserModel.decode_auth_token(request.headers.get('X-API-KEY'))
        user = UserModel.objects.with_id(user_id)
        produit = ProduitModel.product_from_dict(request.json)
        user.add_article(produit)
        return {'result': 'success', 'produit': produit}, 201

@api_rest.route('/produit/<produit_id>')
class Produit(Resource):
    @api_rest.marshal_with(produit_complete_fields)
    @api_rest.response(200, 'Success', produit_complete_fields)
    @api_rest.response(404, 'Ressource not found')
    @validate_ObjectId_or_404('produit_id')
    def get(self, produit_id):
        produit = ProduitModel.objects.with_id(produit_id)
        if produit == None:
            abort(404)
        return produit, 200

    @api_rest.doc(security='apiKey')
    @require_auth(res_type=ResourceType.PRODUIT, id_name='produit_id')
    @api_rest.response(401, 'Unauthorized')
    @api_rest.expect(produit_basic_fields, validate=True)
    @api_rest.response(201, 'Success')
    @api_rest.response(400, 'Validation Error')
    @api_rest.response(404, 'Ressource not found')
    @validate_ObjectId_or_404('produit_id')
    def put(self, produit_id):
        produit = ProduitModel.objects.with_id(produit_id)
        if produit == None:
            abort(404)
        return {'result': 'success'}, 201

    @api_rest.doc(security='apiKey')
    @require_auth(res_type=ResourceType.PRODUIT, id_name='produit_id')
    @api_rest.response(401, 'Unauthorized')
    @api_rest.response(201, 'Success')
    @api_rest.response(404, 'Ressource not found')
    @validate_ObjectId_or_404('produit_id')
    def delete(self, produit_id):
        produit = ProduitModel.objects.with_id(produit_id)
        if produit == None:
            abort(404)
        produit.delete()
        return {'result': 'success'}, 200
