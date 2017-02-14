from google.appengine.ext import db
from blog import *
from models.users import Users
from template import TemplateHandler


class WelcomeHandler(TemplateHandler):
    """ WelcomeHandler will welcome the user once login
    and redirect to the blog page """
    def get(self):
        self.check_user_redirect()
        self.render(
            'welcome.html',
            username=self.username,
            redirect_main=True
            )

