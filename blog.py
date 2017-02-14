#!/usr/bin/env python
# This is the python file (main file) which consist of all classes,
# functions and imported modules.

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
    def valid_reg_check(self,text_input, re_check):
        """ valid_reg_check will match the text_input
        value with regex variables
        """
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
from models.users import Users
from models.blogs import Blogs
from models.comments import Comments
from models.blogvotes import BlogVotes


class BlogFunctions():
    """ BlogFunctions will redirect to specific blog_id
    and checking the login user with blog author """
    def blog_redirect(self, blog_id):
        if not blog_id:
            self.redirect('/blog')
        else:
            self.redirect('/blog/{blog_id}'.format(blog_id=str(blog_id)))

    def blog_author_check(self, blog_id):
        blog = Blogs.blog_by_id(blog_id)

        if not blog or blog.author != self.username:
            self.redirect('/blog')
            return

# Handlers
from handlers.template import TemplateHandler
from handlers.main import MainHandler
from handlers.welcome import WelcomeHandler
from handlers.signup import SignupHandler
from handlers.login import LoginHandler
from handlers.logout import LogoutHandler
from handlers.blogmain import BlogMainHandler
from handlers.newpost import NewPostHandler
from handlers.editpost import EditPostHandler
from handlers.deletepost import DeletePostHandler
from handlers.editcomment import EditCommentHandler
from handlers.deletecomment import DeleteCommentHandler

# Routing
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
