from blog import *
from template import TemplateHandler

class LogoutHandler(TemplateHandler):
    """ This is Class Handler for user logout from blog """
    def get(self):
        self.response.headers.add_header(
            'set-cookie',
            'user_id=; Path=/'
            )
        self.redirect('/blog')

