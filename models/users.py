from google.appengine.ext import db
from blog import CookieFunctions
from blog import *

class Users(db.Model):
    """ Instantiates a class to store user data of
    User table  in the datastore  consisting of
    individual attributes(properties) of the User.
    """
    user_name = db.StringProperty(required=True)
    pw = db.StringProperty(required=True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def entry_and_id(cls, user_name, password, email):
        pw = make_pw_hash(user_name, password)
        new_user = Users(
            user_name=user_name,
            pw=pw,
            email=email
            )
        new_user.put()
        return new_user.key().id()

    @classmethod
    def user_hashed_pw(cls, user_name):
        q = db.GqlQuery("""SELECT *
            from Users
            where user_name = '{name}'
            """.format(name=user_name))
        if q.get():
            return q.get().pw

    @classmethod
    def db_id_from_username(cls, user_name):
        q = db.GqlQuery("""SELECT __key__
            from Users
            where user_name = '{name}'
            """.format(name=user_name))
        if q.get():
            return q.get().id()

    @classmethod
    def login_check(cls, user_name, password):
        h = Users.user_hashed_pw(user_name)
        if h and valid_pw(user_name, password, h):
            return True


