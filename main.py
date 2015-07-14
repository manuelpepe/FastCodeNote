#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

import os
import jinja2

from utils import * # Custom Utils

from google.appengine.ext import db


##### Jinja template configuration ####
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
jinja_env.filters['format_date'] = format_date

class Handler(webapp2.RequestHandler):
    def read_user_cookie(self):
        """ Reads user_id cookie """
        cookie = self.request.cookies.get('user_id')
        if cookie:
            cookie_val = check_secure_val(cookie)
            if cookie_val:
                return int(cookie_val)
        return False

    def initialize(self, *a, **kw):
        """ Runs at every page load """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_user_cookie()
        self.user = uid and User.by_id(int(uid))

    def write(self, *a, **kw):
        """ Shortcut for response.write """
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **params):
        """ Shortcut for rendering templates 
            If the user is logged in its passed as a parameter for the templates."""
        if self.user:
            self.write(self.render_str(template, user = self.user, comment_form = CommentForm(), **params))
        else:
            self.write(self.render_str(template, form_login = LoginForm(), form_signup = SignupForm(), **params))

    def set_hash_cookie(self, name, val):
        """ Sets a cookie with a hashed values """
        cookie_val = make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s' % (name, cookie_val))

    def read_user_cookie(self):
        """ Reads user_id cookie """
        cookie = self.request.cookies.get('user_id')
        if cookie:
            cookie_val = check_secure_val(cookie)
            if cookie_val:
                return int(cookie_val)
        return False

    def login(self, user):
        """ Sets user_id cookie"""
        self.set_hash_cookie('user_id', str(user.key().id()))

    def logout(self):
        """ Deletes user_id cookie """
        self.response.delete_cookie('user_id')

######## Page Handlers ########

class MainPage(Handler):
    def get(self):
        self.render('index.html')

class SignupPage(Handler):
    def get(self):
        if not self.user:
            self.render('signup.html')
        else:
            self.redirect('/')

    def post(self):
        error = None
        form = SignupForm(self.request.POST)
        if form.validate():
            error = validate_signup(form.data)
            if error:
                self.render('signup.html', form = form, error = error)
            else:
                u = User.register(form.data['username'], form.data['password'], form.data['email'])
                u.put()

                self.login(u)
                self.redirect('/')
        else:
            self.render('signup.html', form = form, error = error)

class LoginPage(Handler):
    def get(self):
        if not self.user:
            self.render('login.html')
        else:
            self.redirect('/')

    def post(self):
        error = None
        form = LoginForm(self.request.POST)
        if form.validate():
            error = validate_login(form.data)
            if error:
                self.render('login.html', form = form, error = error)
            else:
                u = User.login(form.data['username'], form.data['password'])
                if u:
                    self.login(u)
                    self.redirect('/')
                else:
                    error = "Invalid login"
                    self.render('login.html', form = form, error = error)
        else:
            self.render('login.html', form = form, error = error)

class LogoutPage(Handler):
    def get(self):
        self.logout()
        self.redirect('/')

class SnippetHomePage(Handler):
    def get(self):
        snippets = snippets_front_cache()
        self.render('snippet_home.html', snippets = snippets, search_form = SimpleSearchForm())

class AddSnippetPage(Handler):
    def get(self):
        if not self.user:
            self.redirect('/login')
        else:
            self.render('addsnippet.html', form = AddSnippetForm(), error = None)

    def post(self):
        error = None
        form = AddSnippetForm(self.request.POST)
        if form.validate():
            s = Snippet(title = form.data['title'], language = form.data['language'], \
                description = form.data['description'], content = form.data['content'], \
                owner = self.user)
            s.put()
            time.sleep(1)
            snippets_front_cache(True)

            self.redirect('/snippets/%s' % s.key().id())
        else:
            self.render('addsnippet.html', form = form, error = error)

class SnippetPermalinkPage(Handler):
    def get(self, sid):
        snippet = Snippet.by_id(sid)
        if not snippet:
            self.error(404)
        else:
            self.render('snippet_permalink.html', snippet = snippet, comments = Snippet.get_comments(sid))

    def post(self, sid):
        form = CommentForm(self.request.POST)
        if form.validate():
            c = Comment(content = form.data['content'], owner = self.user, snippet = Snippet.by_id(sid))
            c.put()

            time.sleep(1)

            self.redirect('/snippets/%s' % sid)

class GroupsPage(Handler):
    def get(self):
        self.render('groups.html', groups = groups_page_cache())
        #g = Group(name = 'test', description = 'test example')
        #g.put()

class AddGroupPage(Handler):
    def get(self):
        if not self.user:
            self.redirect('/login')
        else:
            if self.user.level > 1:
                self.render('addgroup.html', form = AddGroupForm())
            else:
                self.error(401)
                self.redirect('/')

    def post(self):
        error = None
        form = AddGroupForm(self.request.POST)
        if form.validate():
            error = validate_create_group(form.data)
            if error:
                self.render('addgroup.html', form = form, error = error)
            else:
                g = Group(name = form.data['name'], description = form.data['description'])
                g.put()

                time.sleep(1)
                groups_page_cache(True)

                self.redirect('/groups/%s' % g.key().id())
        else:
            self.render('addgroup.html', form = form, error = error)

class GroupPermalinkPage(Handler):
    def get(self, gid):
        group = Group.by_id(gid)
        if not group:
            self.error(404)
        else:
            snippets = group_permalinks_cache(gid)
            self.render('group_permalink.html', group = group, snippets = snippets)

class GroupAddSnippetPage(Handler):
    def get(self, gid):
        if not self.user:
            self.redirect('/login')
        else:
            self.render('addsnippet_togroup.html', form = AddSnippetForm(), group = Group.by_id(gid))

    def post(self, gid):
        form = AddSnippetForm(self.request.POST)
        if form.validate():
            s = Snippet(title = form.data['title'], language = form.data['language'], \
                description = form.data['description'], content = form.data['content'], \
                owner = self.user, parent_group = Group.by_id(gid))
            s.put()

            time.sleep(1)
            snippets_front_cache(True)
            group_permalinks_cache(gid, True)

            self.redirect('/snippets/%s' % s.key().id())
        else:
            self.render('addsnippet_togroup.html', form = form)

class SnippetTopPage(Handler):
    def get(self):
        self.render('wip.html')

class InformationPage(Handler):
    def get(self):
        self.render('info.html')

class ContactPage(Handler):
    def get(self):
        self.render('contact.html', form = ContactForm())

    def post(self):
        error = None
        form = ContactForm(self.request.POST)
        if form.validate():
            error = validate_mail(form)
            if error:
                self.render('contact.html', form = form, error = error)
            else:
                msg = mail.EmailMessage()
                msg.sender = 'BetterTakeThisOff '
                msg.to = 'AndAlsoThis ;)'
                msg.subject = "%s - %s" % (form.data['subject'], form.data['name'])
                msg.body = "%s ------------------ %s " % (form.data['email'], form.data['body'])
                msg.check_initialized()
                msg.send()
                self.render('delivered.html')
        else:
            self.render('contact.html', form = form, error = error)

class SearchPage(Handler):
    def get(self):
        lang = self.request.get('language')
        text = self.request.get('text')
        param = self.request.get('param')

        output = None

        if lang and not text:
            output = Snippet.by_lang(lang)
        if text and not lang:
            if param == 'title':
                output = Snippet.by_title(text)
            elif param == 'description':
                output = Snippet.by_desc(text)

        self.render('search.html', s_form = SimpleSearchForm(), output = output)

class UserPage(Handler):
    def get(self, username):
        u = User.by_name(username)
        if u:
            logging.error(len(User.get_snippets(username)))
            self.render('user_profile.html', res_user = u, snippets = User.get_snippets(username))
        else:
            self.write('user_profile_fail.html', name = username)



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signup/?', SignupPage),
    ('/login/?', LoginPage),
    ('/logout/?', LogoutPage),
    ('/snippets/?', SnippetHomePage),
    ('/snippets/add/?', AddSnippetPage),
    ('/snippets/([0-9]+)/?', SnippetPermalinkPage),
    ('/snippets/top/?', SnippetTopPage),
    ('/groups/?', GroupsPage),
    ('/groups/create/?', AddGroupPage),
    ('/groups/([0-9]+)/?', GroupPermalinkPage),
    ('/groups/([0-9]+)/snippets/add/?', GroupAddSnippetPage),
    ('/info/?', InformationPage),
    ('/contacto/?', ContactPage),
    ('/snippets/search/?', SearchPage),
    ('/user/([a-zA-Z0-9_.-]+)', UserPage)
], debug=True)

