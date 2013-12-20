import cgi
import json
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

api_key = "AIzaSyDiNlzQ9adtA1WojZjE_ZtUJ-u6XenRJ2w"
gcm_url = "https://android.googleapis.com/gcm/send"

class RegistrationId(db.Model):
    registrationId = db.StringProperty(multiline=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')

        registrationIds = db.GqlQuery("SELECT * FROM RegistrationId")

        template_values = { 
            'send_action' : 'send',
            'data' : registrationIds 
        }
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values)) 

class AddRegistrationId(webapp.RequestHandler):
    def post(self):
        registration = RegistrationId()
        
        registration.registrationId = self.request.body
        # :(
        res = db.GqlQuery("SELECT * FROM RegistrationId WHERE registrationId = :1", self.request.body) 
        for item in res:
            return  
        registration.put()        

class SendUserNotification(webapp.RequestHandler):
    def post(self):
        registrationIds = db.GqlQuery("SELECT * FROM RegistrationId")
        arrayIds = []
        for item in registrationIds:
            arrayIds.append(item.registrationId.rstrip('\n'))

        content = cgi.escape(self.request.get('content'))

        gcm_request = { 
            'data' : { 
                'message' : content 
            } , 
            'registration_ids' : arrayIds 
        }
        
        result = urlfetch.fetch(url=gcm_url,
            payload=json.dumps(gcm_request),
            method=urlfetch.POST,
            headers={'Content-Type' : 'application/json', "Authorization" : "key=" + api_key}
        )

        if result.status_code == 200:
            self.redirect('/')
        else: 
            print '' 
            print result.content

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/registration', AddRegistrationId),
                                      ('/send', SendUserNotification)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
