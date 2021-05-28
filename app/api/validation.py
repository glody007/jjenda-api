from bson.objectid import ObjectId
from functools import wraps
from flask import request
from flask_restplus import abort


error_email_and_phone_number = {
                                  "result": "fail",
                                  "errors": {
                                    "email": "'email' or 'phone number' is wrong"
                                  },
                                  "message": "Input payload validation failed"
                                }, 400

error_user_with_same_email = {
                              "result": "fail",
                              "message": "Email already use by another user. Please Log in."
                             }, 202

error_user_with_same_phone_number = {
                                      "result": "fail",
                                      "message": "Phone number already use by another user. Please Log in."
                                    }, 202

error_wrong_credentials = {
                              "result": "fail",
                              "message": "Wrong credentials."
                          }, 404

error_invalid_auth_token = {
                              "result": "fail",
                              "message": "Provide a valid auth token."
                          }, 401

def validate_ObjectId_or_404(id_name):
    def actual_validate_ObjectId_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            id = request.view_args.get(id_name, None)
            if id == None:
                raise KeyError('{} doesnt match any route parameter'.format(id_name))
            if not ObjectId.is_valid(id):
                abort(404)
            return func(*args, **kwargs)
        return wrapper
    return actual_validate_ObjectId_decorator
