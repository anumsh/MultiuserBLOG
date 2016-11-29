#!/usr/bin/env python
# This is the python file (main file) which consist of all classes,
# functions and imported modules.

# importing all modules used for this file

import os
import re
import hmac
import hashlib
import random
import string
import time

import webapp2
# importing jinja2 for templating
import jinja2

# importing google app engine datastore lib storing and
# retrieving attributes values of tables
from google.appengine.ext import db

# VARIABLES

# these 2 lines are for initialising the jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True
    )

# REGEX for sign up form
user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
password_re = re.compile(r"^.{3,20}$")
email_re = re.compile(r"^[\S]+@[\S]+.[\S]+$")


# 'SECRET' to be added for cookie hashing.
SECRET = 'helloworld'


class CookieFunctions():
    """ CookieFunctions will make and validate  cookie ID """
    def hash_str(self, s):
        """  hash_str will return hash string with SECRET value"""
        return hmac.new(SECRET, s).hexdigest()

    def make_cookie_id(self, s):
        """ make_cookie_id will  creates secure cookie string """
        return '{s}|{hash}'.format(s=s, hash=self.hash_str(s))

    def check_cookie_id(self, cookie_id):
        """  check_cookie_id will  check secure cookie string sent by user """
        if cookie_id:
            val = cookie_id.split('|')[0]
            if cookie_id == self.make_cookie_id(val):
                return val

    def give_cookie(self, db_id):
        db_id = self.make_cookie_id(str(db_id))
        self.response.headers.add_header(
            'set-cookie',
            'user_id={db_id}; Path=/'.format(db_id=db_id)
            )

    def username_from_cookie_id(self, cookie_id):
        if self.check_cookie_id(cookie_id):
            user = cookie_id.split('|')[0]
            key = db.Key.from_path('Users', int(user))
            return db.get(key).user_name

    def get_cookie_id(self):
        """ get_template returns the cookie_id"""
        return self.request.cookies.get('user_id')

    # check validity of input based on regex reqs.
    def valid_reg_check(self, text_input, re_check):
        """ valid_reg_check will match the text_input
        value with regex variables  """
        return re_check.match(text_input)


# User Functions
def make_salt():
    """
    make_salt creates a salt for salting passwords
    and other hashed values
    """
    output_str = ''
    for i in range(5):
        output_str += random.choice(string.letters)

    return output_str

def make_pw_hash(name, pw, salt=None):
    """
    make_pw_hash checks if a password salt does not
    exist create one, otherwise hash the
    user data
    """
    if not salt:
        salt = make_salt()

    h = hashlib.sha256(SECRET + name + pw + salt).hexdigest()
    return '{hash_out}|{salt}'.format(
        hash_out=h,
        salt=salt
        )

def valid_pw(name, pw, h):
    """
    valid_pw checks if the password is valid by
    comparing it to a hash
    passed into the function.
    """
    salt = h.split('|')[1]

    if h == make_pw_hash(name, pw, salt):
        return True

# Models
class Users(db.Model):
    """ Instantiates a class to store user data of
    User table  in the datastore  consisting of
    individual attributes(properties) of the User.
    """
    user_name = db.StringProperty(required=True)
    pw = db.StringProperty(required=True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def entry_and_id(cls, user_name, password, email):
        pw = make_pw_hash(user_name, password)
        new_user = Users(
            user_name=user_name,
            pw=pw,
            email=email
            )
        new_user.put()
        return new_user.key().id()

    @classmethod
    def user_hashed_pw(cls, user_name):
        q = db.GqlQuery("""SELECT *
            from Users
            where user_name = '{name}'
            """.format(name=user_name))

        if q.get():
            return q.get().pw

    @classmethod
    def db_id_from_username(cls, user_name):
        q = db.GqlQuery("""SELECT __key__
            from Users
            where user_name = '{name}'
            """.format(name=user_name))
        if q.get():
            return q.get().id()

    @classmethod
    def login_check(cls, user_name, password):
        h = Users.user_hashed_pw(user_name)
        if h and valid_pw(user_name, password, h):
            return True


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
        vote = BlogVotes.all().filter("author =", author).filter("blog_id =", blog_id)
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

# passes uername to all the pages
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

class MainHandler(TemplateHandler):
    """ MainHandler will redirect to main blog page """
    def get(self):
        self.redirect('/blog')

class WelcomeHandler(TemplateHandler):
    """ WelcomeHandler will welcome the user once login
    and redirect to the blog page """
    def get(self):
        self.check_user_redirect()
        self.render(
            'welcome.html',
            username=self.username,
            redirect_main=True
            )


class BlogFunctions():
    """ BlogFunctions will redirect to specific blog_id
    and checking the login user with blog author """
    def blog_redirect(self, blog_id):
        self.redirect('/blog/{blog_id}'.format(blog_id=str(blog_id)))

    def blog_author_check(self, blog, blog_id):
        if not blog:
            self.redirect('/blog')
        elif self.username != blog.author:
            self.blog_redirect(blog_id)


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
            self.redirect('/blog')
            return

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


class EditPostHandler(TemplateHandler, BlogFunctions):
    """ This is Class Handler for  editing of blog posts """
    def get(self, blog_id):
        """ uses get request to get newpost.html """
        blog = Blogs.blog_by_id(blog_id)
        self.blog_author_check(blog, blog_id)

        self.render(
            'edit-post.html',
            blog=blog,
            delete_post='/blog/{blog_id}/delete'.format(blog_id=str(blog_id))
            )

    def post(self, blog_id):
        """handles the POST request from newpost.html"""
        title = self.request.get('subject')
        content = self.request.get('content')
        blog = Blogs.blog_by_id(blog_id)

        if title and content and self.username == blog.author:
            blog.edit(title, content)
            self.blog_redirect(blog_id)
        else:
            error = 'Need both title and content'
            self.render(
                'edit-post.html',
                blog={'title': '', 'content': ''},
                blog_title=title,
                blog_content=content,
                error=error)


class DeletePostHandler(TemplateHandler, BlogFunctions):
    """ This is Class Handler for  deleting of blog posts """
    def get(self, blog_id):
        blog = Blogs.blog_by_id(blog_id)
        self.blog_author_check(blog, blog_id)

        self.render(
            'delete-post.html',
            blog=blog
            )

    def post(self, blog_id):
        blog = Blogs.blog_by_id(blog_id)
        self.blog_author_check(blog, blog_id)

        delete = self.request.get('delete')

        if delete == 'Yes':
            blog.delete()
            self.redirect('/blog')
        else:
            self.blog_redirect(blog_id)


class EditCommentHandler(TemplateHandler, BlogFunctions):
    """ This is Class Handler for  editing the comments """
    def get(self, comment_id):
        comment = Comments.comment_by_id(comment_id)

        if not comment or comment.author != self.username:
            self.redirect('/blog')
            return

        self.render(
            'edit-comment.html',
            comment=comment
            )

    def post(self, comment_id):
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


class DeleteCommentHandler(TemplateHandler, BlogFunctions):
    """ This is Class Handler for deleting the comments """
    def get(self, comment_id):
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
        comment = Comments.comment_by_id(comment_id)

        if not comment or comment.author != self.username:
            self.redirect('/blog')
            return

        delete = self.request.get('delete')

        if delete == 'Yes':
            comment.delete()
            time.sleep(1)

        self.blog_redirect(comment.blog_post)


class SignupHandler(TemplateHandler):
    """ This is Class Handler for  registering on blog """
    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        password_verify = self.request.get('verify')
        email = self.request.get('email')

        valid_input = True

        params = {
            'user': username,
            'email': email
        }

        if Users.user_hashed_pw(username):
            params['username_error'] = "Username already exist."
            valid_input = False

        if not self.valid_reg_check(username, user_re):
            params['username_error'] = "Not a valid username."
            valid_input = False

        if not self.valid_reg_check(password, password_re):
            params['password_error'] = "Not a valid password."
            valid_input = False
        elif password != password_verify:
            params['password_mismatch'] = "Passwords didn't match."
            valid_input = False

        if email and not self.valid_reg_check(email, email_re):
            params['email_error'] = "Not a valid email"
            valid_input = False

        if username and password and password_verify and valid_input:
            db_id = Users.entry_and_id(username, password, email)
            self.give_cookie(db_id)
            self.redirect('/blog/welcome')
        else:
            self.render(
                'signup.html',
                **params
                )


class LoginHandler(TemplateHandler):
    """ This is Class Handler for login into user blog """
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        if Users.login_check(username, password):
            user_id = Users.db_id_from_username(username)
            self.give_cookie(user_id)
            self.redirect('/blog/welcome')
        else:
            self.render('login.html', login_error='Invalid login information.')


class LogoutHandler(TemplateHandler):
    """ This is Class Handler for user logout from blog """
    def get(self):
        self.response.headers.add_header(
            'set-cookie',
            'user_id=; Path=/'
            )
        self.redirect('/blog')



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogMainHandler),
    ('/blog/newpost', NewPostHandler),
    ('/blog/welcome', WelcomeHandler),
    ('/blog/signup', SignupHandler),
    ('/blog/login', LoginHandler),
    ('/blog/logout', LogoutHandler),
    webapp2.Route(r'/blog/<blog_id:\d+>', BlogMainHandler),
    webapp2.Route(r'/blog/<blog_id:\d+>/edit', EditPostHandler),
    webapp2.Route(r'/blog/<blog_id:\d+>/delete', DeletePostHandler),
    webapp2.Route(r'/blog/<comment_id:\d+>/cmt-del', DeleteCommentHandler),
    webapp2.Route(r'/blog/<comment_id:\d+>/cmt-edt', EditCommentHandler)
], debug=True)
