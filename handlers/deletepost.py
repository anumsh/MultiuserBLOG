from google.appengine.ext import db
from blog import *
from models.blogs import Blogs
from models.users import Users
from template import TemplateHandler
from blog import BlogFunctions

class DeletePostHandler(TemplateHandler, BlogFunctions):
    """ This is Class Handler for  deleting of blog posts """
    
    def get(self, blog_id):
	self.check_user_redirect()
	blog = Blogs.blog_by_id(blog_id)
        self.blog_author_check(blog_id)

        self.render(
            'delete-post.html',
            blog=blog
            )

    def post(self, blog_id):
	self.check_user_redirect()
	blog = Blogs.blog_by_id(blog_id)
        self.blog_author_check(blog_id)

        delete = self.request.get('delete')

        if delete == 'Yes':
            blog.delete()
            self.redirect('/blog')
        else:
            self.blog_redirect(blog_id)

