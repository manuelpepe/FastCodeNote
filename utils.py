################### UTILITIES FILE ###################
#
#             Custom codes and functions
#
######################################################

import re
import hashlib
import hmac
import random
import string
import logging
import time
from configs import *
from forms import *
from db_models import * # Custom Database Models

from google.appengine.api import memcache
from google.appengine.api import mail

#### Regexs ####
USER_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")
PASS_RE = re.compile(r".")
EMAIL_RE = re.compile(r"^\S+@\S+\.\S")

#### Hashing ####
# Password Hashing 
def make_salt():
    """ Makes random salt """
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
    """ Make hash value for the pw """
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s|%s" % (salt, h)

def check_valid_pw(name, pw, hash):
    """ Checks pw hash value """
    old = hash.split('|')[0]
    return make_pw_hash(name, pw, old).split('|')[1] == hash.split('|')[1]

# Cookie Hashing
def hash_str(s):
    """ Returns a hashed value of a string + secret """
    return hmac.new(SECRET_WORD, str(s)).hexdigest()

def make_secure_val(s):
    """ Returns the string concadenated with the hashed value. 
        Ready to set in the cookie"""
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    """ Checks the cookie and, if the cookie is valid, returns the value """
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val

#### Validations ####
def validate_signup(data):
    """ Validate form with Regexs and test if the user exist """
    username = str(data['username'])
    if not User.by_name(username):
        password = str(data['password'])
        email = str(data['email'])

        if USER_RE.match(username) and PASS_RE.match(password):
            if email:
                if not EMAIL_RE.match(email):
                    return "The email field is not required, but if you choose to fill it, it should be valid"
        else:
            return "Invalid username or password."
    else:
        return "User already exist"

def validate_login(data):
    """ Validate login with Regexs """
    username = str(data['username'])
    password = str(data['password'])

    if not USER_RE.match(username) and PASS_RE.match(password):

        return "Invalid username or password"
    return None

def validate_create_group(data):
    """ Validate the creation of a group with Regex.
    Wip as it doesn't do anything now"""
    return None

def validate_mail(data):
    name = str(data['name'])
    email = str(data['email'])
    subject = str(data['subject'])
    body = str(data['body'])

    if not EMAIL_RE.match(email):
        if name and subject and body:
            return None
        else:
            return "Todos los campos son necesarios"
    else:
        return "Email no valido"

#### Cache Functions ####
def snippets_front_cache(update = False):
    """ If update is False: gets cache from the front page.
    If update is True or there is no cache: query database and updates cache """
    key = 'snippets_front'
    time.sleep(1)
    snippets = memcache.get(key)
    if update or snippets is None:
        snippets = Snippet.get_all()
        snippets = list(snippets)
        memcache.set(key, snippets)
    return snippets

def groups_page_cache(update = False):
    """ This updates the groups page when a new group is created. """
    key = "groups_page"
    time.sleep(1)
    groups = memcache.get(key)
    if update or groups is None:
        groups = Group.get_all()
        groups = list(groups)
        memcache.set(key, groups)
    return groups

def group_permalinks_cache(group_id, update = False):
    """ If update is False: gets cache from the given group.
    If update is True or there is no cache: query database and updates cache """
    key = str(group_id)
    time.sleep(1) # this is to make sure cache is correctly updated
    snippets = memcache.get(key)
    if update or snippets is None:
        snippets = Group.get_snippets_by_group_id(group_id)
        snippets = list(snippets)
        memcache.set(key, snippets)
    return snippets

#### Rate Limit Functions ####
def identifiers():
    ret = ['ip' + self.request.remote_addr]
    if self.user:
        ret.append('user:%s' % self.user.key().id())
    return ret

def over_limit(conn, duration = 3600, limit = 2400):
    # WIP!
    pass

#### Jinja Filters ####
def format_date(value):
    """ Returns only the date on format YYYY-MM-DD """
    value = str(value)
    return value.split(' ')[0]

#### Random Functions ####
def get_date():
    """ Returns formatted date YYYY/mm/dd """
    return time.strftime("%Y-%m-%d")