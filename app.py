import os 
import secrets

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
from blocklist import BLOCKLIST
# import models 

# #models need to have been imported so sqlalchemy can create our tables

#same as models.__init__
#can just say models because imports are in __init__

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

#creates flask app
#allows you to run app
#makes endpoints available to client

#application factory pattern
#can call function whenever you need, includign for when you want to write tests for your flask app
#call the function istead of running the file to create a new flask app

#databse url argument in case you want to connect to a database
def create_app(db_url=None):
    app = Flask(__name__)

    #configuration variables
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config['API_VERSION'] = "v1"
    app.config['OPENAPI_VERSION'] = '3.0.3'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    #if db_url exists, use that, otherwise, use the next one
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

    #initializes flask sqlalchemy extension
    db.init_app(app)

    #has to be creatd after db.init_app
    migrate = Migrate(app, db)
    api = Api(app)

    #secret key used for signing JWTs 
    #app can check secret key and verify that JWT was generated by THIS app
    #make sure user hasn't created their own jwt somewhere else

    #this would generate a new secret key every time
    # app.config["JWT_SECRET_KEY"] = secrets.SystemRandom().getrandbits(128)

    #get this by running function above in python terminal
    #usually deployed in an envrionment variable (gitignore)
    app.config["JWT_SECRET_KEY"] = "202818376306308343738149448109322603617"


    jwt = JWTManager(app)

    #If this function returns True, the request is termined, and user will get error 
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in BLOCKLIST

    #message that is sent when function above returns true
    @jwt.revoked_token_loader
    def revoked_token_callabck(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description":"The token has been revoked.", "error":"token_reovked"}
            ),
            401,
        )

    #expected a fresh otken, but got a non-fresh token
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header,jwt_payload):    
        return (
            jsonify(
                {
                    "description":"The token is not fresh.",
                    "error":"fresh_token_required"
                }
            )
        )
    #claims are less commonly used
    #runs every time you create an access token
    #allows you to do some work when you create the jwt, instead of when you use the jwt
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # would be better to look in database and see whether the user is an admin
        if identity == 1:
            return {"is_admin":True}
        return {"is_admin":False}


    # returned when jwt has expired
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message":"The token has expired.", "error":"token_expired"},401,)
        )

    #erorr argument is for when there is no JWT or it is not valid
    #payload and header cannot be extracted from jwt if it's not there
    # if token was invalid
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message":"Signature verification failed.","error":"invalid_token"}
            ),
            401,
        )

    #if token was missing 
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description":"Request does not contain access token.",
                    "error":"authorization_required"
                }
            ),
            401,
        )
    
    with app.app_context():
        import models  # noqa: F401

        db.create_all()


    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app


#DATABSE
#all database providers use connection string that contain information that allow the client to connect to the database (flask app is client)


