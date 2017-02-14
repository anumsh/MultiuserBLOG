from google.appengine.ext import db
from blog import *
from models.blogs import Blogs
from models.users import Users
from models.comments import Comments
from template import TemplateHandler
from blog import BlogFunctions

class DeleteCommentHandler(TemplateHandler, BlogFunctions):
    """ This is Class Handler for deleting the comments """
   
    def get(self, comment_id):
	self.check_user_redirect()
        comment = Comments.comment_by_id(comment_id)

        if not comment or comment.author != self.username:
            self.redirect('/blog')
            return

        blog = Blogs.blog_by_id(comment.blog_post)
        self.render(
            'delete-comment.html',
            comment=comment,
            blog=blog
            )

    
    def post(self, comment_id):
	self.check_user_redirect()
        comment = Comments.comment_by_id(comment_id)

        if not comment or comment.author != self.username:
            self.redirect('/blog')
            return

        delete = self.request.get('delete')

        if delete == 'Yes':
            comment.delete()
            time.sleep(1)

        self.blog_redirect(comment.blog_post)

