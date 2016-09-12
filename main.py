import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainBlog(Handler):
    def render_mainBlog(self, posts=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")

        self.render("mainBlog.html", posts = posts)

    def get(self):
        self.render_mainBlog()

class NewPost(Handler):
    def render_newPost(self, title="", body="", error=""):
        self.render("newPost.html", title=title, body=body, error=error)

    def get(self):
        self.render_newPost()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            p = Post(title = title, body = body)
            p.put()

            self.redirect("/blog/{}".format(p.key().id()))

        else:
            error = "Please give your post some content and a title!!"
            self.render_newPost(title, body, error)

class ViewPostHandler(Handler):

    def get(self, post_id):
        post = Post.get_by_id(int(post_id))

        if not post:
            error = "Sorry, there is no post at this location.  Please try a different ID."
            self.response.write(error)
            return

        self.render('viewPost.html', post = post)


app = webapp2.WSGIApplication([
    ('/blog', MainBlog),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<post_id:\d+>', ViewPostHandler)
], debug=True)
