from google.appengine.ext import db
from blog import *
from models.users import Users
from models.blogs import Blogs
from models.comments import Comments
from models.blogvotes import BlogVotes
from template import TemplateHandler
from blog import BlogFunctions

class BlogMainHandler(TemplateHandler, BlogFunctions):
    """ BlogMainHandler will handles the /blog page and
    /blog/blog_id pages """
    def build_vote_dict(self, blog_iterable):
        vote_dict = {}

        for blog in blog_iterable:
            blog_id = blog.key().id()
            liked = BlogVotes.vote_check(self.username, blog_id).get()

            vote_dict[blog.key().id()] = [
                BlogVotes.vote_count(blog_id),
                liked
            ]

        return vote_dict

    def get_all_blogs_page(self, like_error=None):
        blogs = Blogs.get_blogs(10)
        print blogs
        vote_dict = self.build_vote_dict(blogs)

        self.render(
            'main-page.html',
            blogs=blogs,
            vote_dict=vote_dict,
            like_error=like_error
        )

    def get_single_blog_page(self, blog_id, error='', like_error=''):
        blog = Blogs.blog_by_id(blog_id)
        comments_list = Comments.get_comments(int(blog_id), 20)

        # handles case of incorrect blog_id in url.
        if not blog:
            return self.redirect('/blog')
            

        # put [blog] into a list to work with build_vote_dict
        vote_dict = self.build_vote_dict([blog])
        time_diff = (blog.last_modified - blog.created).total_seconds()
        self.render(
            'blog-post.html',
            blog=blog,
            vote_dict=vote_dict,
            comments_list=comments_list,
            time_diff=time_diff,
            edit_url='/blog/{blog_id}/edit'.format(blog_id=blog_id),
            error=error,
            like_error=like_error
            )

    def get(self, blog_id=None):
        if blog_id:
            # Handles the /blog/#### case.
            self.get_single_blog_page(blog_id)
        else:
            self.get_all_blogs_page()

    # Note - must handle both /blog and /blog/#### cases
    # as users can submit a "like" on a blog post on the /blog main page.
    def post(self, blog_id=None):
        if blog_id:
            blog = Blogs.blog_by_id(blog_id)
        else:
            blog = None

        # like_error default None.
        # will be list, with blog_id and actual error message as items
        # template checks if blog_id matches, then displays error.
        like_error = None
        like = self.request.get('like')
        unlike = self.request.get('unlike')
        comment_submit = self.request.get('comment-submit')

        # first checks if like/liked is posted by user.
        if like:
            vote = BlogVotes.vote_check(self.username, int(like))
            like_error = [int(like)]
            if not self.username:
                like_error.append('Please Login to like')
            elif vote.get():
                like_error.append("You can like once .")
            # this elif is the success case.
            elif self.username != Blogs.blog_by_id(like).author:
                BlogVotes.vote_entry(self.username, int(like))
                # added a 1 second sleep delay
                # to allow time for datastore to update.
                time.sleep(1)
            else:
                like_error.append("You can't like your own post!")
        elif unlike:
            vote = BlogVotes.vote_check(self.username, int(unlike))
            if vote.get():
                vote.get().delete()
            time.sleep(1)

        # Checks if not individual blog page.  Causes re-render at this point.
        if not blog:
            self.get_all_blogs_page(like_error)
            return

        # All below are for /blog/##### individual pages.
        content = self.request.get('comment-content')
        valid_comment = True

        error = ''

        # checks for comment post
        if comment_submit:
            if not self.username:
                error = 'Please Login  to comment'
                valid_comment = False
            elif not content:
                error = 'PLease enter some text'
                valid_comment = False

            if valid_comment:
                Comments.entry_and_id(
                    int(blog_id),
                    content,
                    self.username
                    )
                time.sleep(1)

        self.get_single_blog_page(blog_id, error, like_error)

