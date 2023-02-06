from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema
from flask_jwt_extended import jwt_required

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import StoreModel

blp = Blueprint("Stores",__name__,description="Operations on stores")

#connects methods this endpoint
@blp.route("/store/<int:store_id>")
class Store(MethodView):

    @jwt_required()
    @blp.response(201, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store 

    @jwt_required()
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return{"message":f'The store {store.name} was deleted'}

    
@blp.route("/store")
class StoresList(MethodView):

    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):

        return StoreModel.query.all()
        # return stores.values()
        #return {"stores":list(stores.values())}

    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def post(self, store_data):
        

        #NO LONGER NEEDED
        #make sure name key is included
        # if "name" not in store_data:
        #     abort(
        #         400,
        #         message="Bade request. Make sure 'name' is included"
        #     )
        
        #make sure the store name isn't already included
        # for store in stores.values():
        #     if store_data["name"] == store["name"]:
        #         abort(400, "That store already exists")

        #UUID
        # store_id = uuid.uuid4().hex

        # ** will unpack values and store them in new dictionary
        # similar functioanlity to spread operator in python, expect for dictionaries instead of arrays
        # store = {**store_data, "id":store_id}
        # stores[store_id] = store
        # return store, 201 
        #201 = data has been accepted 

        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
            #this error is for when you try to add somethign to the database that would cause an inconsistency in the data, that would violate constraints 
        except IntegrityError:
            abort(400,message="A store with that name already exists")
        except SQLAlchemyError:
            abort(500, message="There was an error adding this store")

        return store


#marshmallow can turn dictionary and object into json