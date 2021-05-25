from mongoengine import *
from flask_login import UserMixin
from bson.json_util import dumps
import os, datetime, calendar
from geopy.geocoders import Nominatim


if os.getenv("FLASK_ENV") == "development":
    connect(host="mongodb://127.0.0.1:27017/dev_db")
elif os.getenv("FLASK_ENV") == "test":
    db = connect('jjenda-test-database', host='db')
else:
    db = connect(host=os.getenv("DB_URI"))

class UserType:
    ENREGISTRER  = "enregistrer"
    ADMIN = "admin"

class CustomDateTimeField(DateTimeField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_json(self):
        return str("dyglo")


class PlanType:
    GRATUIT = {"NOM" : "GRATUIT", "NBR_ARTICLES" : 4,
               "PRICE" : "0$", "ADVANTAGE" : "4 articles gratuits par mois"}
    STANDARD = {"NOM" : "STANDARD", "NBR_ARTICLES" : 30,
                "PRICE" : "5$", "ADVANTAGE" : "30 articles par mois"}
    GOLD = {"NOM" : "GOLD", "NBR_ARTICLES" : 100,
            "PRICE" : "10$", "ADVANTAGE" : "100 articles par mois"}

    @staticmethod
    def all():
        return [PlanType.GRATUIT, PlanType.STANDARD, PlanType.GOLD]

class SourceType:
    USER = "user"
    CRAWLER = "crawler"


class Plan(Document):
    nbr_articles_restant = IntField(required=True, default=PlanType.GRATUIT["NBR_ARTICLES"])
    type = StringField(required=True, default=PlanType.GRATUIT["NOM"])
    timestamp_end = DateTimeField(required=True)
    end_at = StringField(required=True)
    user = ReferenceField('User')

    def set_user(self, user):
        self.user = user
        self.save()

    @staticmethod
    def create(plan_type=PlanType.GRATUIT):
        end_date = Plan.end_date(plan_type)
        plan = Plan(type=plan_type["NOM"],
                    nbr_articles_restant=plan_type["NBR_ARTICLES"],
                    timestamp_end=end_date,
                    end_at=str(end_date))
        plan.save()
        return plan

    def is_ended(self):
        now = datetime.datetime.now()
        end = self.timestamp_end
        if (datetime.date(now.year, now.month, now.day) >
            datetime.date(end.year, end.month, end.day)):
            return True
        else:
            return False


    @staticmethod
    def end_date(plan_type=PlanType.GRATUIT):
        now = datetime.datetime.now()
        if plan_type["NOM"] == PlanType.GRATUIT["NOM"]:
            month_end_day = calendar.monthrange(now.year, now.month)[1]
            return datetime.datetime(now.year, now.month, month_end_day)
        else:
            return now + datetime.timedelta(days=30)

    def can_post_article(self):
        if self.nbr_articles_restant > 0:
            return True
        return False

    def post_article(self):
        if self.can_post_article():
            self.nbr_articles_restant -= 1
            self.save()
        else:
            raise ValueError("Nombre articles restant 0")


class ProduitBrut(Document):
    categorie = StringField(max_length=50)
    prix = IntField(required=True)
    description = StringField(required=True, max_length=200)
    url_photo = StringField(required=True)
    location = StringField(required=True, default="Lubumbashi")
    saler_number = StringField(min_length=10, max_length=13)
    saler_name = StringField(required=True, min_length=3, max_length=50)
    timestamp = DateTimeField(required=True, default=datetime.datetime.utcnow())
    created_at = StringField(required=True, default=str(datetime.datetime.utcnow()))

    @staticmethod
    def from_dict(dict):
        data_time = datetime.datetime.utcnow()
        return ProduitBrut(categorie=dict['categorie'],
                           prix=dict['prix'],
                           description=dict['description'],
                           url_photo=dict['url_photo'],
                           location=dict['location'],
                           saler_number=dict['saler_number'],
                           saler_name=dict['saler_name'],
                           timestamp=data_time,
                           created_at=str(data_time))

    @staticmethod
    def add(json):
        produit = ProduitBrut.from_dict(json)
        produit.save()
        return produit

    @staticmethod
    def from_list(list):
        for dict in list:
            ProduitBrut.add(dict)

    @staticmethod
    def fromFile(file):
        import json

        data = json.load(file)
        produitsRaw = ProduitBrut.from_list(data['products_raw'])

    @staticmethod
    def page(page_nb=1, items_per_page=20):
        offset = (page_nb - 1) * items_per_page
        return ProduitBrut.objects.skip( offset ).limit( items_per_page )

geolocator = Nominatim(user_agent="glodymbutwile@gmail.com")

class Produit(Document):
    categorie = StringField(required=True, max_length=50)
    vendeur_id = StringField(required=True)
    prix = IntField(required=True)
    description = StringField(required=True, max_length=200)
    url_photo = StringField(required=True)
    url_thumbnail_photo = StringField(required=True)
    location = GeoPointField()
    location_name = StringField()
    city = StringField()
    timestamp = DateTimeField(required=True, default=datetime.datetime.utcnow())
    created_at = StringField(required=True, default=str(datetime.datetime.utcnow()))
    source =  StringField(required=True, default=SourceType.USER)

    @staticmethod
    def product_from_dict(dict):
        data_time = datetime.datetime.utcnow()
        longitude = float(dict['longitude'])
        latitude = float(dict['latitude'])
        loc_name = Produit.location_name_from_location(latitude, longitude)
        return Produit(prix=dict['prix'],
                       vendeur_id="",
                       categorie=dict['categorie'],
                       description=dict['description'],
                       url_photo=dict['url_photo'],
                       url_thumbnail_photo=dict['url_thumbnail_photo'],
                       timestamp=data_time,
                       created_at=str(data_time),
                       location=[longitude, latitude],
                       location_name=loc_name)

    @staticmethod
    def location_from_city(city):
        try:
            loc = geolocator.geocode(city)
            return {"location" : [loc.longitude, loc.latitude], "name" : loc[0]}
        except:
            return {"location" : [27.4826264, -11.6642316],
                    "name" : "Lubumbashi, Makutano, Lubumbashi, Ville de Lubumbashi, Haut-Katanga, République démocratique du Congo"}

    @staticmethod
    def location_name_from_location(latitude, longitude):
        try:
            loc = geolocator.reverse(latitude, longitude)
            return loc[0]
        except:
            return "Lubumbashi, Makutano, Lubumbashi, Ville de Lubumbashi, Haut-Katanga, République démocratique du Congo"


    @staticmethod
    def from_product_raw(product_raw):
        loc = Produit.location_from_city(product_raw.location)
        return Produit(prix=product_raw.prix,
                       vendeur_id="",
                       categorie=product_raw.categorie,
                       description=product_raw.description,
                       url_photo=product_raw.url_photo,
                       url_thumbnail_photo=product_raw.url_photo,
                       timestamp=product_raw.timestamp,
                       created_at=product_raw.created_at,
                       location=loc["location"],
                       location_name=loc["name"])

    def to_dict(self):
        return {'id': self.id,
                'prix': self.prix,
                'vendeur_id': self.vendeur_id,
                'categorie': self.categorie,
                'description': self.description,
                'url_photo': self.url_photo,
                'url_thumbnail_photo': self.url_thumbnail_photo,
                'timestamp': self.timestamp,
                'created_at': self.created_at,
                'location': self.location}

    def to_algolia_record(self):
        produit = self.to_dict()
        produit['objectID'] = str(produit['id'])
        return produit

    @queryset_manager
    def order_by_created_desc(doc_cls, queryset, page_nb = 1, items_per_page = 10):
        offset = (page_nb - 1) * items_per_page
        return queryset.order_by('-timestamp').skip( offset ).limit( items_per_page )

    @staticmethod
    def near_order_by_created_desc(loc=[0, 0], max_distance=1000):
        return Produit.order_by_created_desc.filter(location__near=loc, location__max_distance=max_distance)

    @staticmethod
    def near_order_by_distance(loc=[0, 0], max_distance=1000):
        return Produit.objects.filter(location__near=loc, location__max_distance=max_distance).order_by('location')

    @staticmethod
    def page(page_nb=1, items_per_page=20):
        offset = (page_nb - 1) * items_per_page
        return Produit.objects.skip( offset ).limit( items_per_page )

    @staticmethod
    def best_match(loc=[0, 0], max_distance=1000, nbr=200, page_nb = 1, items_per_page = 10):
        offset = (page_nb - 1) * nbr
        return Produit.near_order_by_distance(loc=loc, max_distance=max_distance)\
                    .limit(nbr).order_by('-timestamp').skip(offset).limit(items_per_page)

class User(Document, UserMixin):
    unique_id = StringField(required=True)
    nom = StringField(required=True, min_length=3, max_length=50)
    phone_number =StringField(min_length=10, max_length=13)
    email = EmailField(min_length=10)
    url_photo = URLField(min_length=10)
    localisation = GeoPointField()
    produits = ListField(ReferenceField(Produit))
    plan = ReferenceField(Plan)
    source =  StringField(required=True, default=SourceType.USER)

    @staticmethod
    def insert(user, plan_type):
        user.save()
        user.set_plan(Plan.create(plan_type=plan_type))
        return user

    @staticmethod
    def from_user_info(user_info):
        user =  User(unique_id = str(user_info["sub"]),
                     nom = user_info["given_name"],
                     email = user_info["email"],
                     url_photo = user_info["picture"])
        user.save()
        user.set_plan(Plan.create())
        return user

    @staticmethod
    def from_product_raw(product_raw):
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
        article.vendeur_id = self.unique_id
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

    def get_id(self):
        return self.unique_id
