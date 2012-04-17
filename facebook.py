## fb.py
##
## Facebook class to retrieve the user informations, after login on 
## FlightPooling app
##
## Author: Rafael Lucas

import json
import oauth2 as oauth
import urlparse, urllib

# Error Class
class FBError(Exception):
    """ Facebook class error

        All the errors (exceptions) getting on the code will be
        redirected to here
    """
    
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class FB(object):
    """ Facebook class

        This is the main class that handle with facebook login and informations
        about the user. 	  
    """

    callback_url =      None
    request_token_url= None
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    redirect_uri = 'http://beta.flightpooling.com/'
    consumer = None
    request_token_params={'scope': 'email'}
    _request_token = None
    _access_token = None

    def __init__(self, consumer_key, consumer_secret, callback_url):
        """ Constructor. """
        self.consumer = oauth.Consumer(consumer_key, consumer_secret)
        self.callback_url = callback_url
        
    def get_authorize_url(self):
        """ get_authorize_url() method

            Will send to user an dialog authorization on facebook to get the 
            informations after it. First the method verifies the user access_token
            and after send a url, asking for authorization.

            \return The url after processing by get_authorize_url() method.
        """

        return "%s?scope=email&redirect_uri=%s&client_id=%s" % (self.authorize_url, self.redirect_uri, self.consumer.key)
    
    def verifier(self,code):
        """ verifier() method

            Will check the user access token and set an existent token.
        """
        
        client = oauth.Client(self.consumer)
        resp, content = client.request(self.access_token_url, "POST")
        if resp['status'] != '200':
            print resp
            raise FBError("Invalid response %s." % resp['status'])
        access_token = dict(urlparse.parse_qsl(content))
        self._access_token = access_token
        
    def get_profile(self,fields=('id','first-name','last-name','headline','summary')):
        """ get_profile() method

            This method get the user information and returns it using
            JSON format.

            \return the user informations in JSON format.
        """

        if not self._access_token:
            raise FBError("Authentication needed!")
            
        token = oauth.Token(self._access_token['oauth_token'], self._access_token['oauth_token_secret'])
        client = oauth.Client(self.consumer, token)
        profile_url = self.profile_url % ",".join(fields)
        resp, content = client.request(profile_url,headers={"x-li-format":'json'})
        
        if resp['status'] != '200':
            print resp
            raise FBError("Invalid response %s." % resp['status'])
        
        try:
            return json.loads(content)
        except Exception, e:
            raise FBError("Invalid json %s." % unicode(e))
