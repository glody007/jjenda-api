""" API Blueprint Application """

from flask import Blueprint, current_app
from .security  import authorizations
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask_restplus import Api

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')
api_rest = Api(api_bp, authorizations=authorizations)

@api_bp.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


# Import resources to ensure view is registered
from .produit import *
from .user import *
from .auth import *
