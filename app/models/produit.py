from mongoengine import *
import datetime
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="glodymbutwile@gmail.com")

class SourceType:
    USER = "user"
    CRAWLER = "crawler"

class Produit(Document):
    categorie = StringField(required=True, max_length=50)
    vendeur_id = StringField(required=True, default="")
    prix_initial = IntField(required=True)
    prix_actuel = IntField(required=True)
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
        return Produit(prix_initial=dict['prix'],
                       prix_actuel=dict['prix'],
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
    def insert(product):
        product.save()

    @staticmethod
    def from_product_raw(product_raw):
        loc = Produit.location_from_city(product_raw.location)
        return Produit(prix_initial=product_raw.prix,
                       prix_actuel=product_raw.prix,
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
                'prix_initial': self.prix_initial,
                'prix_actuel': self.prix_actuel,
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
