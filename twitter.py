## twitter.py
##
## Twitter class to retrieve the user informations, after login on 
## FlightPooling app
##
## Author: Rafael Lucas

import json
import oauth2 as oauth
import urlparse, urllib

#Errer Class
class TwiterError(Exception):
    """ Twitter class error

        All the errors (exceptions) getting on the code will be
        redirected to here
    """

    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class Twiter(object):
    """ Twitter class

        This is the main class that handle with twitter login and informations
        about the user.           
    """

    callback_url =      None
    base_url='http://api.twitter.com/1/',
    request_token_url='http://api.twitter.com/oauth/request_token',
    access_token_url='http://api.twitter.com/oauth/access_token',
    authorize_url='http://api.twitter.com/oauth/authenticate',
    consumer = None
    _request_token = None
    _access_token = None    

    def __init__(self, consumer_key, consumer_secret, callback_url):
        """ Constructor. """

        self.consumer = oauth.Consumer(consumer_key, consumer_secret)
        self.callback_url = callback_url
        
    def request_token(self):
        """ request_token() method
            
            This method will retrieve the user request_token and set an existent
            parameter.
        """

        client = oauth.Client(self.consumer)
        resp, content = client.request(self.request_token_url, "POST", 
                                       body=urllib.urlencode({'oauth_callback':self.callback_url}))
    
        if resp['status'] != '200':
            raise TwiterError("Invalid response %s." % resp['status'])
        
        request_token = dict(urlparse.parse_qsl(content))
        self._request_token = request_token
        
    def get_authorize_url(self):
        """ get_authorize_url() method

            Will send to user an dialog authorization on twitter to get the 
            informations after it. First the method verifies the user access_token
            and after send a url, asking for authorization.

            \return The url after processing by get_authorize_url() method.
        """

        if not self._request_token:
            self.request_token()
        return "%s??oauth_token=%s" % (self.authorize_url, self._request_token['oauth_token'])
    
    def verifier(self, code):
        """ verifier() method

            Will check the user access token and set an existent token.
        """

        
        if not self._request_token:
            self.request_token()

        token = oauth.Token(self._request_token['oauth_token'], self._request_token['oauth_token_secret'])
        token.set_verifier(code)
        client = oauth.Client(self.consumer, token)
        resp, content = client.request(self.access_token_url, "POST")
        if resp['status'] != '200':
            print resp
            raise TwiterError("Invalid response %s." % resp['status'])
        access_token = dict(urlparse.parse_qsl(content))
        self._access_token = access_token
        
    def get_profile(self,fields=('id','first-name','last-name','headline','summary')):
        """ get_profile() method

            This method get the user information and returns it using
            JSON format.

            \return the user informations in JSON format.
        """

        if not self._access_token:
            raise TwiterError("Authentication needed!")
            
        token = oauth.Token(self._access_token['oauth_token'], self._access_token['oauth_token_secret'])
        client = oauth.Client(self.consumer, token)
        profile_url = self.profile_url % ",".join(fields)
        resp, content = client.request(profile_url,headers={"x-li-format":'json'})
        
        if resp['status'] != '200':
            print resp
            raise TwiterError("Invalid response %s." % resp['status'])
        
        try:
            return json.loads(content)
        except Exception, e:
            raise TwiterError("Invalid json %s." % unicode(e))
