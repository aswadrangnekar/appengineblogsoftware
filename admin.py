"""
Google App Engine Script that handles administration screens for the
blog.
"""

import cgi
import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from models import *
import request

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class ShowArticlesHandler(request.BlogRequestHandler):
    """
    Handles the main admin page, which lists all articles in the blog,
    with links to their corresponding edit pages.
    """
    def get(self):
        articles = Article.get_all()
        template_vars = {'articles' : articles}
        self.response.out.write(self.render_template('admin-main.html',
                                                     template_vars))

class NewArticleHandler(request.BlogRequestHandler):
    """
    Handles requests to create and edit a new article.
    """
    def get(self):
        article = Article(title='New article',
                          body='Content goes here',
                          draft=True)
        template_vars = {'article' : article}
        self.response.out.write(self.render_template('admin-edit.html',
                                                     template_vars))

class SaveArticleHandler(request.BlogRequestHandler):
    """
    Handles form submissions to save an edited article.
    """
    def post(self):
        title = cgi.escape(self.request.get('title'))
        body = self.request.get('content')
        s_id = cgi.escape(self.request.get('id'))
        id = int(s_id) if s_id else None
        tags = cgi.escape(self.request.get('tags'))
        published_when = cgi.escape(self.request.get('published_when'))
        draft = cgi.escape(self.request.get('draft'))
        if tags:
            tags = [t.strip() for t in tags.split(',')]
        else:
            tags = []
        tags = Article.convert_string_tags(tags)

        if not draft:
            draft = False
        else:
            draft = (draft.lower() == 'on')

        article = Article.get(id) if id else None
        if article:
            # It's an edit of an existing item.
            just_published = article.draft and (not draft)
            article.title = title
            article.body = body
            article.tags = tags
            article.draft = draft
        else:
            # It's new.
            article = Article(title=title,
                              body=body,
                              tags=tags,
                              draft=draft)
            just_published = not draft

        article.save()

        edit_again = cgi.escape(self.request.get('edit_again'))
        edit_again = edit_again and (edit_again.lower() == 'true')
        if edit_again:
            self.redirect('/admin/article/edit/?id=%s' % article.id)
        else:
            self.redirect('/admin/')

class EditArticleHandler(request.BlogRequestHandler):
    """
    Handles requests to edit an article.
    """
    def get(self):
        id = int(self.request.get('id'))
        article = Article.get(id)
        if not article:
            raise ValueError, 'Article with ID %d does not exist.' % id

        article.tag_string = ', '.join(article.tags)
        template_vars = {'article'  : article}
        self.response.out.write(self.render_template('admin-edit.html',
                                                     template_vars))

class DeleteArticleHandler(request.BlogRequestHandler):
    """
    Handles form submissions to delete an article.
    """
    def get(self):
        id = int(self.request.get('id'))
        article = Article.get(id)
        if article:
            article.delete()

        self.redirect('/admin/')

# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

application = webapp.WSGIApplication(
    [('/admin/?', ShowArticlesHandler),
     ('/admin/article/new/?', NewArticleHandler),
     ('/admin/article/delete/?', DeleteArticleHandler),
     ('/admin/article/save/?', SaveArticleHandler),
     ('/admin/article/edit/?', EditArticleHandler),
     ],

    debug=True)

def main():
    util.run_wsgi_app(application)

if __name__ == "__main__":
    main()
