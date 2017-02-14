from google.appengine.ext import db
from blog import * 

class BlogVotes(db.Model):
    """
    Instantiates a class to store votes (entity) data
    for BlogVotes table in the datastore consisting
    of individual attributes/properties of the post.
     """
    author = db.StringProperty(required=True)
    blog_id = db.IntegerProperty(required=True)
    vote = db.IntegerProperty(default=1)

    @classmethod
    def vote_entry(cls, author, blog_id):
        new_vote = BlogVotes(
            author=author,
            blog_id=blog_id
            )

        new_vote.put()
        return new_vote.key().id()

    @classmethod
    def vote_check(cls, author, blog_id):
        vote = BlogVotes.all().filter("author =", author).filter("blog_id =",    blog_id)
        return vote

    @classmethod
    def vote_count(cls, blog_id):
        count_list = db.GqlQuery("""SELECT *
            from BlogVotes
            where blog_id = {blog_id}
            """.format(blog_id=blog_id)
        )

        count_val = 0
        for item in count_list:
            count_val += item.vote

        return count_val
