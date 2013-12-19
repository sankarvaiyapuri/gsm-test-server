import cgi
import json
import os
import logging

from sets import Set
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import urlfetch

api_key = "AIzaSyDiNlzQ9adtA1WojZjE_ZtUJ-u6XenRJ2w"
gcm_url = "https://android.googleapis.com/gcm/send"

def get_gcm_request(message_text, package):
    
    registrationIds = ""

    if "" == package or None == package:
        registrationIds = db.GqlQuery("SELECT * FROM RegistrationId")
    else:
        registrationIds = db.GqlQuery("SELECT * FROM RegistrationId where package = :1", package)

    arrayIds = []
    for item in registrationIds:
        arrayIds.append(item.registrationId.rstrip('\n'))
        #content = cgi.escape(self.request.get('content'))

    gcm_request = { 
        'data' : { 
            'message' : message_text
        }, 
        'registration_ids' : arrayIds 
     }
   
    return json.dumps(gcm_request),

def get_unique_package():
    registrationIds = db.GqlQuery("SELECT * FROM RegistrationId")
    s = Set([])
    for item in registrationIds:
        s.add(item.package)
    return s 

class RegistrationId(db.Model):
    registrationId = db.StringProperty(multiline=False)
    package = db.StringProperty(multiline=False)

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')
        
        package = self.request.get('package')
        registrationIds = db.GqlQuery("SELECT * FROM RegistrationId")

        text_area = get_gcm_request('You Message', package)[0]
        packages = get_unique_package()
        template_values = { 
            'send_action' : 'send',
            'data' : packages,
            'text_area' : text_area
        }
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values)) 
    

class AddRegistrationId(webapp.RequestHandler):
    def get(self):
        registration = RegistrationId() 
        
        registration.registrationId = self.request.get('id')
        registration.package = self.request.get('package')
        
        #:(
        res = db.GqlQuery("SELECT * FROM RegistrationId WHERE registrationId = :1", registration.registrationId ) 
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
            headers = { 'Content-Type' : 'application/json', "Authorization" : "key=" + api_key }
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
