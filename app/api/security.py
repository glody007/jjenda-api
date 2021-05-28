""" Security Related things """
from functools import wraps
from flask import request
from flask_restplus import abort
from bson.objectid import ObjectId
from ..models import User, UserType, Produit
from .validation import error_invalid_auth_token
from .resource_type import ResourceType

authorizations = {
    'apiKey' : {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    }
}

class AuthType:
    REGULAR = "regular"
    ADMIN = "admin"

def is_authorized(user_id, auth_type, res_type="", id_name=""):
    user = User.objects.with_id(user_id)
    if user == None:
        return False
    # Admin give access
    elif user.type == UserType.ADMIN:
        return True
    # Require admin but not admin
    elif auth_type == AuthType.ADMIN:
        return False
    else:
        if res_type == "":
            return True
        # Test if id_name is in url
        id = request.view_args.get(id_name, None)
        if id == None:
            raise KeyError('{} doesnt match any route parameter'.format(id_name))
        if not ObjectId.is_valid(id):
            abort(404)
        if res_type == ResourceType.USER:
            return str(user.id) == id
        else:
            produit = Produit.objects.with_id(id)
            if produit == None:
                abort(404)
            return str(user.id) == produit.vendeur_id



def require_auth(type=AuthType.REGULAR, res_type="", id_name=""):
    def actual_require_auth_decorator(func):
        """ Secure method decorator """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if token in header
            auth_token = request.headers.get('X-API-KEY')
            if auth_token:
                # Check if token is valid
                resp = User.decode_auth_token(auth_token)
                if ObjectId.is_valid(resp):
                    if is_authorized(resp, type, res_type, id_name):
                        return func(*args, **kwargs)
                    else:
                        return abort(401)
                else:
                    return {
                              "result": "fail",
                              "message": resp
                           }, 401
            else:
                return error_invalid_auth_token
        return wrapper
    return actual_require_auth_decorator
