import jinja2
import os
import logging
import webapp2
from google.appengine.ext import ndb
from wtforms.ext.appengine.ndb import model_form
from google.appengine.ext.webapp.util import run_wsgi_app
from webapp2_extras import sessions


# Define an example model and add a record.
class Contact(ndb.Model):
   modified = ndb.DateTimeProperty(required=True,auto_now=True)
   created = ndb.DateTimeProperty(required=True,auto_now_add=True)
   state = ndb.StringProperty(required=True)
   key_name = ndb.StringProperty(required=True)
   name = ndb.StringProperty(required=True)
   city = ndb.StringProperty()
   age = ndb.IntegerProperty(required=True)
   is_admin = ndb.BooleanProperty(default=False)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = \
    jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

#jinja_environment = jinja2.Environment(autoescape=True,
#    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)
        
    def render_template(
        self,
        filename,
        template_values,
        **template_args
        ):
        template = jinja_environment.get_template(filename)
        self.response.out.write(template.render(template_values))

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class ViewHomePage(BaseHandler):
    def post(self):
        return self.get_or_post()

    def get(self):
        return self.get_or_post()

    def get_or_post(self):
        if self.request.POST:
            new_entity = Contact(key_name=self.request.get('key_name'), name=self.request.get('name'), age=int(self.request.get('age')), state=self.request.get('state'))
            new_entity.put()

        # Generate a form based on the model.
        ContactForm = model_form(Contact)

        # Get a form populated with entity data.
        #entity = Contact.get_by_key_name('test')
        #keys = ['test']
        #entity = ndb.get_multi([ndb.Key('Contact', 'test')])
        entitylist = Contact.query().order(-Contact.created).fetch(1)
        logging.info('QQQ: entitylist: %s' % entitylist)
        if len(entitylist) > 0:
            form = ContactForm(obj=entitylist[0])
        else:
            form = ContactForm()

        #Properties from the model can be excluded from the generated form, or it can
        #include just a set of properties. For example:
        #
        #.. code-block:: python
        
        # Generate a form based on the model, excluding 'city' and 'is_admin'.
        ContactForm = model_form(Contact, exclude=('city', 'is_admin'))
        
        # or...
        
        # Generate a form based on the model, only including 'name' and 'age'.
        ContactForm = model_form(Contact, only=('name', 'age'))

        #The form can be generated setting field arguments:
        #
        #.. code-block:: python
        #
        ContactForm = model_form(Contact, only=('name', 'age'), field_args={
           'name': {
               'label': 'Full name',
               'description': 'Your name',
           },
           'age': {
               'label': 'Age',
               #'validators': [validators.NumberRange(min=14, max=99)],
           }
        })
        logging.info('contactform3: %s' % ContactForm)
        #self.response.out.write('contactform3: %s' % ContactForm)
        template_values = {
                'form': form}
        template = jinja_environment.get_template('stdpage_block.html')
        self.response.out.write(template.render(template_values))

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([
    ('/', ViewHomePage),
    ],
                config=config,
                debug=True)

def main():
    run_wsgi_app(app)

if __name__ == '__main__':
    main()
