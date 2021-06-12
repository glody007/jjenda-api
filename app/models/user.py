from mongoengine import *
from .produit import *
from .plan import *
import datetime
import os
import jwt
from flask_bcrypt import generate_password_hash, check_password_hash

class UserType:
    ENREGISTRER  = "enregistrer"
    ADMIN = "admin"

class User(Document):
    type = StringField(required=True, default=UserType.ENREGISTRER)
    nom = StringField(required=True, min_length=3, max_length=50)
    source =  StringField(required=True, default=SourceType.USER)
    phone_number = StringField(required=True, min_length=10, max_length=13)
    password_hash = StringField(min_length=20)
    email = EmailField(min_length=10)
    url_photo = URLField(min_length=10)
    localisation = GeoPointField()
    produits = ListField(ReferenceField(Produit))
    plan = ReferenceField(Plan)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def encode_auth_token(self):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=300, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': str(self.id)
            }
            return jwt.encode(
                payload,
                os.getenv('SECRET_KEY', 'my_precious'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, os.getenv('SECRET_KEY', 'my_precious'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    @staticmethod
    def insert(user, plan_type=PlanType.STANDARD):
        user.save()
        user.set_plan(Plan.create(plan_type=plan_type))
        return user

    @staticmethod
    def from_user_info(user_info):
        user =  User(nom = user_info["nom"],
                     phone_number = user_info["phone_number"],
                     email = user_info["email"])
        return user


    def set_admin(self):
        self.type = UserType.ADMIN
        self.save()

    @staticmethod
    def register(user_info):
        user =  User(nom = user_info["nom"],
                     phone_number = user_info["phone_number"],
                     email = user_info["email"],
                     password_hash = generate_password_hash(user_info["password"], 12).decode('utf-8'))
        User.insert(user)
        return user

    @staticmethod
    def register_admin(user_info):
        user = User.objects(email=user_info["email"]).first()
        if user == None:
            user = User.register(user_info)
            user.set_admin()
        return user

    def update_from_info(self, user_info):
        self.nom = user_info['nom']
        self.phone_number = user_info['phone_number']
        self.email = user_info['email']
        self.save()

    @staticmethod
    def from_raw(product_raw):
        user = User(nom = product_raw.saler_name,
                    phone_number = product_raw.saler_number,
                    source = SourceType.CRAWLER,
                    unique_id=product_raw.saler_number)
        user.save()
        user.set_plan(Plan.create())
        return user

    def can_post_article(self):
        return self.plan.can_post_article()

    def nbr_articles_restant(self):
        self.refresh_plan_if_end()
        return self.plan.nbr_articles_restant

    def set_plan(self, plan):
        plan.set_user(self)
        self.plan = plan
        self.save()

    def add_article_from_dict(self, dict):
        produit = Produit.product_from_dict(dict)
        self.add_article(produit)
        return produit

    def add_article(self, article):
        self.refresh_plan_if_end()
        self.plan.post_article()
        article.vendeur_id = str(self.id)
        article.save()
        self.produits.append(article)
        self.save()
        return article

    def refresh_plan_if_end(self):
        if self.plan == None:
            self.set_plan(Plan.create())
        elif self.plan.is_ended():
            self.set_plan(Plan.create())

    def articles_to_json(self):
        return Produit.objects(vendeur_id=self.unique_id).to_json()
