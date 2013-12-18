import cgi
import json
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

api_key = "AIzaSyDiNlzQ9adtA1WojZjE_ZtUJ-u6XenRJ2w"

registrationIds = "APA91bH91lUn-xpYLc4x098J3lH3BPqM54tLXdv0STLkJlvGPNvv1xga0wO_YZhkTNImvmrMuHZn5G8A8qaYnF-t-U14xupKado0SxvNt4d15Psyf8LJQvXzANNjRcK7sQ6JoxL2TxTUNJWxNU9GYzQf8BdjSqq_WeO09UfkufkdJNds6GuURys"


class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
          <html>
            <body>
              <form action="/send" method="post">
                <div><textarea name="content" rows="3" cols="60"></textarea></div>
                <div><input type="submit" value="Sign Guestbook"></div>
              </form>
            </body>
          </html>""")


class Guestbook(webapp.RequestHandler):
    def post(self):
        content = cgi.escape(self.request.get('content'));
        
        self.response.out.write('<html><body>You wrote:<pre>')
        self.response.out.write(content)
        self.response.out.write('</pre></body></html>')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/send', Guestbook)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

