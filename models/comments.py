from google.appengine.ext import db
from blog import * 

class Comments(db.Model):
    """
    Instantiates a class to store comments(entity) data
    for Comments (table) in the datastore consisting
    of individual attributes/properties of the post.
    """

    blog_post = db.IntegerProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty(default='Anonymous')
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def entry_and_id(cls, blog_id, content, author):
        new_comment = Comments(
            blog_post=blog_id,
            content=content,
            author=author
            )
        new_comment.put()
        return new_comment.key().id()

    @classmethod
    def comment_by_id(cls, comment_id):
        key = db.Key.from_path('Comments', int(comment_id))
        comment = db.get(key)
        return comment

    def edit(self, content):
        self.content = content
        self.put()

    @classmethod
    def get_comments(cls, blog_id, count):
        comments_list = db.GqlQuery("""SELECT *
            from Comments
            where blog_post = {blog_id}
            order by created desc
            limit {count}
            """.format(
            blog_id=blog_id,
            count=count
            )
        )
        return comments_list


