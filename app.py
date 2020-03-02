import uuid
from flask import Flask,redirect, url_for
from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime
import os

app = Flask(__name__)

mongohost = os.getenv("MONGO_HOST","localhost")
mongoport = os.getenv("MONGO_PORT",27017)
mongo = MongoClient(mongohost, int(mongoport))
db = mongo.logs_db

gob_digital = OAuth2ConsumerBlueprint(
	"gob_digital", __name__,
	client_id= os.getenv("CLIENT_ID"),
	client_secret=os.getenv("CLIENT_SECRET"),
	token_url="https://accounts.claveunica.gob.cl/openid/token",
	authorization_url="https://accounts.claveunica.gob.cl/openid/authorize",
	scope=["openid","run","name"],
	authorized_url="/login_azenteno/claveunica/authorized"
)
app.register_blueprint(gob_digital)

@oauth_authorized.connect
def logged_in(blueprint, token):
	resp = blueprint.session.post("https://www.claveunica.gob.cl/openid/userinfo")
	objeto = resp.json()
	objeto["date"] = datetime.datetime.now()
	db.logs.insert_one(objeto)

@app.route("/")
def index():
	if not gob_digital.session.token:
		return redirect(url_for('gob_digital.login'))
	resp = gob_digital.session.post("https://www.claveunica.gob.cl/openid/userinfo")
	return resp.json()

if __name__ == "__main__":
	
	load_dotenv()
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

	app.secret_key = uuid.uuid4().hex
	app.run(debug=True)

