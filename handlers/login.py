from google.appengine.ext import db
from blog import *
from blog import CookieFunctions
from models.users import Users
from template import TemplateHandler

class LoginHandler(TemplateHandler):
    """ This is Class Handler for login into user blog """
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        if Users.login_check(username, password):
            user_id = Users.db_id_from_username(username)
            self.give_cookie(user_id)
            self.redirect('/blog/welcome')
        else:
            self.render('login.html', login_error='Invalid login information.')
