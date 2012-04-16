from flask import Flask, request, redirect, url_for, session, flash, g, \
     render_template
from flaskext.oauth import OAuth

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# configuration
DATABASE_URI = 'sqlite:////tmp/flask-oauth.db'
SECRET_KEY = 'development key'
DEBUG = True

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

# Use Twitter as example remote application
twitter = oauth.remote_app('twitter',
    base_url='http://api.twitter.com/1/',
    request_token_url='http://api.twitter.com/oauth/request_token',
    access_token_url='http://api.twitter.com/oauth/access_token',
    authorize_url='http://api.twitter.com/oauth/authenticate',
    consumer_key=TWITTER_CONSUMER_KEY,
    consumer_secret=TWITTER_SECRET_KEY
)

# setup sqlalchemy
engine = create_engine(DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'users'
    id = Column('user_id', Integer, primary_key=True)
    name = Column(String(60))
    oauth_token = Column(String(200))
    oauth_secret = Column(String(200))

    def __init__(self, name):
        self.name = name


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@twitter.tokengetter
def get_twitter_token():
    user = g.user
    if user is not None:
        return user.oauth_token, user.oauth_secret


@app.route('/')
def index():
    tweets = None
    if g.user is not None:
        resp = twitter.get('statuses/home_timeline.json')
        if resp.status == 200:
            tweets = resp.data
        else:
            flash('Unable to load tweets from Twitter. Maybe out of '
                  'API calls or Twitter is overloaded.')
    return render_template('index.html', tweets=tweets)


@app.route('/tweet', methods=['POST'])
def tweet():
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={
        'status':       status
    })
    if resp.status == 403:
        flash('Your tweet was too long.')
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))


@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    user = User.query.filter_by(name=resp['screen_name']).first()

    if user is None:
        user = User(resp['screen_name'])
        db_session.add(user)

    user.oauth_token = resp['oauth_token']
    user.oauth_secret = resp['oauth_token_secret']
    db_session.commit()

    session['user_id'] = user.id
    flash('You were signed in')
    return redirect(next_url)


if __name__ == '__main__':
    app.run()
