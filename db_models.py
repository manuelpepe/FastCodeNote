from google.appengine.ext import db
import utils

class User(db.Model):
    username = db.StringProperty(required = True)
    pwhash = db.StringProperty(required = True)
    email = db.EmailProperty
    level = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(required = True, auto_now = True)

    @classmethod
    def by_id(cls, uid):
        """ Returns user by id """
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, username):
        """ Returns user by name """
        u = User.all().filter('username = ', username).get()
        return u

    @classmethod
    def register(cls, username, pw, email = None):
        """ Create user tuple, doesn't store it in the database"""
        pwhash = utils.make_pw_hash(username, pw)
        return User(username = username, pwhash = pwhash, email = email, level = 1)

    @classmethod
    def login(cls, username, pw):
        """ Checks if an user exist, if it does, returns the user object """
        u = cls.by_name(username)
        if u and utils.check_valid_pw(username, pw, u.pwhash):
            return u

    @classmethod
    def get_snippets(cls, username, amount = None):
        """ Returns a given amount of the snippets from a given user """
        try:
            return cls.by_name(username).snippets.order('-created').fetch(amount)
        except AttributeError:
            return False

    @classmethod
    def get_comments(cls, username, amount):
        """ Returns a given amount of the comments from a given user"""
        pass

class Group(db.Model):
    name = db.StringProperty(required = True)
    description = db.StringProperty(required = True)
    created = db.DateTimeProperty(required = True, auto_now_add = True)

    @classmethod
    def by_id(cls, group_id):
        """ Returns a group by its id """
        return cls.get_by_id(int(group_id))

    @classmethod
    def get_all(cls):
        """ Returns all groups """
        return cls.all().order('-created')

    @classmethod
    def get_snippets_by_group_id(cls, group_id, amount = None):
        """ Gets a given amount of snippets of a group """
        try:
            return cls.by_id(group_id).snippets.order('-created').fetch(amount)
        except AttributeError:
            return False

class Snippet(db.Model):
    title = db.StringProperty(required = True)
    language = db.StringProperty(required = True)
    description = db.TextProperty(required = True)
    content = db.TextProperty(required = True)
    last_edited = db.DateTimeProperty(auto_now = True)
    created = db.DateTimeProperty(auto_now_add = True)
    owner = db.ReferenceProperty(User, collection_name='snippets', required = True)
    parent_group = db.ReferenceProperty(Group, collection_name='snippets')

    @classmethod
    def get_all(cls):
        """ Returns all snippets """
        return cls.all().order('-created')

    @classmethod
    def by_id(cls, snippet_id):
        """ Returns snippet by id """
        return Snippet.get_by_id(int(snippet_id))

    @classmethod
    def by_lang(cls, lang):
        return Snippet.all().filter('language =', lang).run()

    @classmethod
    def by_title(cls, search):
        return Snippet.all().filter('title =', search).run()

    @classmethod
    def by_desc(cls, search):
        return Snippet.all().filter('description = ', search).run()

    @classmethod
    def get_comments(cls, snippet_id, amount = None):
        """ Returns a given amount of comments from a given snippet """
        try:
            return cls.by_id(snippet_id).comments.fetch(amount)
        except AttributeError:
            return False

    @classmethod
    def get_votes(cls, snippet_id):
        """ Returns all votes from a given snippet """
        try:
            return cls.by_id(snippet_id).snippet_votes.fetch(None)
        except AttributeError:
            return False


class Comment(db.Model):
    content = db.TextProperty(required = True)
    owner = db.ReferenceProperty(User, collection_name='comments')
    snippet = db.ReferenceProperty(Snippet, collection_name='comments')

    @classmethod
    def get_votes(cls, comment_id):
        """ Get the all votes of a comment """
        try:
            return cls.by_id(comment_id).comment_votes.fetch(None)
        except AttributeError:
            return False


class Votes_Comments(db.Model):
    direction = db.BooleanProperty(required = True)
    id_comment = db.ReferenceProperty(Comment, collection_name = 'comment_votes')
    id_user = db.ReferenceProperty(User, collection_name='comment_votes')

class Votes_Snippets(db.Model):
    direction = db.BooleanProperty(required = True)
    id_snippet = db.ReferenceProperty(Snippet, collection_name = 'snippet_votes')
    id_user = db.ReferenceProperty(User, collection_name='snippet_votes')
    
