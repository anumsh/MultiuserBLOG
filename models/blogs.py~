from google.appengine.ext import db
from blog import *

class Blogs(db.Model):
    """
    Instantiates a class to store post data for Blogs
    in the datastore consisting of individual
    attributes/propertiesof the post.
    """
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    @classmethod
    def get_blogs(cls, limit, offset=0):
        blogs = db.GqlQuery("""SELECT *
            from Blogs
            order by created desc
            limit {limit_num}
            offset {offset_num}
            """.format(
            limit_num=limit,
            offset_num=offset
            )
        )
        return blogs

    @classmethod
    def entry_and_id(cls, title, content, user_name):
        new_blog = Blogs(
            title=title,
            content=content,
            author=user_name
            )
        new_blog.put()
        return new_blog.key().id()

    @classmethod
    def blog_by_id(cls, blog_id):
        key = db.Key.from_path('Blogs', int(blog_id))
        blog = db.get(key)
        return blog

    def edit(self, title, content):
        self.title = title
        self.content = content
        self.put()

