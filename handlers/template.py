import webapp2
import jinja2
from blog import *
from blog import CookieFunctions


# This TemplateHandler contains methods used across many pages.
# All other handlers inherit from this class.
class TemplateHandler(webapp2.RequestHandler, CookieFunctions):
    """
     TemplateHandler class is  for rendering any templates.
    """
    def write(self, *a, **kw):
        """write function keeps away from writing
        self.reponse.out all the time"""
        self.response.out.write(*a, **kw)

# passes username to all the pages
    def render_str(self, template, **params):
        """ render_str takes the template name and
        some parameters to subsitute into template """
        t = jinja_env.get_template(template)
        params['username'] = self.username
        return t.render(params)

    def render(self, template, **kw):
        """ render calls the write and render_str to
        print out the template """
        self.write(self.render_str(template, **kw))

# all pages will always have self.username
# based on user's cookie_id
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        self.username = self.username_from_cookie_id(self.get_cookie_id())

    def check_user_redirect(self):
        """
        check_user_redirect redirects to signup
         page if user is not login
         """
        if not self.username:
            self.redirect('/blog/signup')

