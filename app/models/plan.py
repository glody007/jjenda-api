from mongoengine import *
import datetime, calendar

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
