import datetime
import functools
import os
import re
import urllib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import (Flask, flash, Markup, redirect, render_template, request,
                   Response, session, url_for)
from flask_mail import Mail, Message
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from peewee import *
from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list
from playhouse.sqlite_ext import *
    

APP_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE = 'sqliteext:///%s' % os.path.join(APP_DIR, 'blog.db')
DEBUG = True


# For Micawber rich content
SITE_WIDTH = 800

# Create Flask WSGI app
app = Flask(__name__)
app.config.from_pyfile('config.py')

SECRET_KEY = app.config.get("SECRET_KEY")
ADMIN_PASSWORD = app.config.get("ADMIN_PASSWORD")

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = app.config.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = app.config.get("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


mail = Mail(app)
app.config.from_object(__name__)

# wrapper for peewee DB
flask_db = FlaskDB(app)
database = flask_db.database

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc)
oembed_providers = bootstrap_basic(OEmbedCache())


class Entry(flask_db.Model):
    title = CharField()
    slug = CharField(unique=True)
    content = TextField()
    published = BooleanField(index=True)
    timestamp = DateTimeField(default=datetime.datetime.now, index=True)

    @property
    def html_content(self):

        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=app.config['SITE_WIDTH'])
        return Markup(oembed_content)

    def save(self, *args, **kwargs):
        # Generate URL-friendly rep of entry's title.
        if not self.slug:
            self.slug = re.sub(r'[^\w]+', '-', self.title.lower()).strip('-')
        ret = super(Entry, self).save(*args, **kwargs)

        # Store search content.
        self.update_search_index()
        return ret

    def update_search_index(self):
        # Create row in FTSEntry table. Allows search
        exists = (FTSEntry
                  .select(FTSEntry.docid)
                  .where(FTSEntry.docid == self.id)
                  .exists())
        content = '\n'.join((self.title, self.content))
        if exists:
            (FTSEntry
             .update({FTSEntry.content: content})
             .where(FTSEntry.docid == self.id)
             .execute())
        else:
            FTSEntry.insert({
                FTSEntry.docid: self.id,
                FTSEntry.content: content}).execute()

    @classmethod
    def public(cls):
        return Entry.select().where(Entry.published == True)

    @classmethod
    def drafts(cls):
        return Entry.select().where(Entry.published == False)

    @classmethod
    def search(cls, query):
        words = [word.strip() for word in query.split() if word.strip()]
        if not words:
            # Return an empty query.
            return Entry.noop()
        else:
            search = ' '.join(words)

        # Query the full-text search index for entries matching the given
        # search query, then join the actual Entry data on the matching
        # search result.
        return (Entry
                .select(Entry, FTSEntry.rank().alias('score'))
                .join(FTSEntry, on=(Entry.id == FTSEntry.docid))
                .where(
                    FTSEntry.match(search) &
                    (Entry.published == True))
                .order_by(SQL('score')))


class FTSEntry(FTSModel):
    content = TextField()

    class Meta:
        database = database


def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner


@app.route('/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')

        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)

@app.route('/requestpassword', methods = ["GET", "POST"])
def requestpass():
    if request.method=="POST" and request.form.get('thegoodword') and request.form.get("email"):
        thegoodword = "Reliable Rhinos is the best pod!"
        email = request.form.get('email')
        emails = ["mshen63@gatech.edu","kunal.kushwaha@majorleaguehacking.com", "will@majorleaguehacking.com", "abeaboagye7@gmail.com","ayana.nithey@gmail.com"
                  "charbel.breydyts@udlap.mx", "dakshinabp@gmail.com", "derya.1kilic.3@gmail.com", "emilyxinyi.chen@mail.utoronto.ca",
                  "gina10111@hotmail.com", "irodrigoro@gmail.com", "lalohdez77@gmail.com", "thuanhsone99@gmail.com", "truongnguyenlinh@outlook.com", "wangela472@gmail.com"]
        userinput = request.form.get('thegoodword')
        if userinput==thegoodword and email in emails:
            flash("Check your Email! You should've gotten the ~secret password~ to log in!", 'success')
            me = "blogrhinos@gmail.com"
            my_password = "hellorhinos"
            you = email

            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Alert"
            msg['From'] = me
            msg['To'] = "blogrhinos@gmail.com"

            html = '<html><body><p>Shh! The passcode is <u>reliablerhinos</u></p></body></html>'
            part2 = MIMEText(html, 'html')

            msg.attach(part2)
            s = smtplib.SMTP_SSL('smtp.gmail.com',465)
            # uncomment if interested in the actual smtp conversation
            # s.set_debuglevel(1)
            s.login(me, my_password)

            s.sendmail(me, you, msg.as_string())
            s.quit()

        else:
            flash("Please use your Reliable Rhinos email and make sure you typed the phrase exactly as shown!", 'danger')
        
    return render_template('requestaccount.html')
    


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('logout.html')


@app.route('/')
def index():
    search_query = request.args.get('q')
    if search_query:
        query = Entry.search(search_query)
    else:
        query = Entry.public().order_by(Entry.timestamp.desc())

    return object_list(
        'index.html',
        query,
        search=search_query,
        check_bounds=False)


@app.route('/michelle')
def michelle():
    return render_template("michelle.html", url=os.getenv("URL"))


@app.route('/emily')
def emily():
    return render_template("emily.html", url=os.getenv("URL"))


def _create_or_edit(entry, template):
    if request.method == 'POST':
        entry.title = request.form.get('title') or ''
        entry.content = request.form.get('content') or ''
        entry.published = request.form.get('published') or False
        if not (entry.title and entry.content):
            flash('Title and Content are required.', 'danger')
        else:
         
            try:
                with database.atomic():
                    entry.save()
            except IntegrityError:
                flash('Error: this title is already in use.', 'danger')
            else:
                flash('Entry saved successfully.', 'success')
                if entry.published:
                    return redirect(url_for('detail', slug=entry.slug))
                else:
                    return redirect(url_for('edit', slug=entry.slug))

    return render_template(template, entry=entry)


@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    return _create_or_edit(Entry(title='', content=''), 'create.html')


@app.route('/drafts/')
@login_required
def drafts():
    query = Entry.drafts().order_by(Entry.timestamp.desc())
    return object_list('index.html', query, check_bounds=False)


@app.route('/<slug>/')
def detail(slug):
    if session.get('logged_in'):
        query = Entry.select()
    else:
        query = Entry.public()
    entry = get_object_or_404(query, Entry.slug == slug)
    return render_template('detail.html', entry=entry)


@app.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = get_object_or_404(Entry, Entry.slug == slug)
    return _create_or_edit(entry, 'edit.html')


@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
   
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.urlencode(querystring)


@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404


def main():
    database.create_tables([Entry, FTSEntry], safe=True)
    app.run(debug=True)

def getApp():
    return app
