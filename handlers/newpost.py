from google.appengine.ext import db
from blog import *
from models.users import Users
from models.blogs import Blogs
from template import TemplateHandler
from blog import BlogFunctions

class NewPostHandler(TemplateHandler, BlogFunctions):
    """ This is the handler class for the new blog post page """
    def get(self):
        """
        uses GET request to render newpost.html by calling
        render from the
        TemplateHandler class
        """
	self.check_user_redirect()
        self.render('newpost.html')

    
    def post(self):
        """ handles the POST request from newpost.html"""
	self.check_user_redirect()
        title = self.request.get('subject')
        content = self.request.get('content')

        if title and content:
            blog_id = Blogs.entry_and_id(
                title,
                content,
                self.username
                )
            time.sleep(1)
            self.blog_redirect(blog_id)
        else:
            error = 'Need both title and content'
            self.render(
                'newpost.html',
                blog_title=title,
                blog_content=content,
                error=error)

