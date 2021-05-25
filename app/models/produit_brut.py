from mongoengine import *

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
