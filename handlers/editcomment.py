from google.appengine.ext import db
from blog import *
from models.users import Users
from models.comments import Comments
from template import TemplateHandler
from blog import BlogFunctions

class EditCommentHandler(TemplateHandler, BlogFunctions):
    """ This is Class Handler for  editing the comments """
    
    def get(self, comment_id):
        self.check_user_redirect()
        comment = Comments.comment_by_id(comment_id)

        if not comment or comment.author != self.username:
            self.redirect('/blog')
            return

        self.render(
            'edit-comment.html',
            comment=comment
            )
     
    
    def post(self, comment_id):
	self.check_user_redirect()
        comment = Comments.comment_by_id(comment_id)

        if not comment or comment.author != self.username:
            self.redirect('/blog')
            return

        comment_content = self.request.get('comment-content')

        if not comment_content:
            error = 'Please enter some text'
            self.render(
                'edit-comment.html',
                comment=comment,
                error=error
                )
        else:
            comment.edit(comment_content)
            time.sleep(1)
            self.blog_redirect(comment.blog_post)


