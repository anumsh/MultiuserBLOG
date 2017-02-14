from google.appengine.ext import db
from blog import *
from models.users import Users
from template import TemplateHandler
from blog import CookieFunctions

class SignupHandler(TemplateHandler):
    """ This is Class Handler for  registering on blog """
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        password_verify = self.request.get('verify')
        email = self.request.get('email')

        valid_input = True

        params = {
            'user': username,
            'email': email
        }

        if Users.user_hashed_pw(username):
            params['username_error'] = "Username already exist."
            valid_input = False

        if not self.valid_reg_check(username, user_re):
            params['username_error'] = "Not a valid username."
            valid_input = False

        if not self.valid_reg_check(password, password_re):
            params['password_error'] = "Not a valid password."
            valid_input = False
        elif password != password_verify:
            params['password_mismatch'] = "Passwords didn't match."
            valid_input = False

        if email and not self.valid_reg_check(email, email_re):
            params['email_error'] = "Not a valid email"
            valid_input = False

        if username and password and password_verify and valid_input:
            db_id = Users.entry_and_id(username, password, email)
            self.give_cookie(db_id)
            self.redirect('/blog/welcome')
        else:
            self.render(
                'signup.html',
                **params
                )


