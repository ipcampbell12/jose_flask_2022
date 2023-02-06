
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import ItemSchema, ItemUpdateSchema
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel

blp = Blueprint("Items",__name__,description="Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):

    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self,item_id):

        #query attribute comes from db.Model, from flask_sqlalchemy
        #retrieves item from database using primary key
        item = ItemModel.query.get_or_404(item_id)
        return item 

    @jwt_required()
    def delete(self, item_id):

        #using jwt claim
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required")

        item = ItemModel.query.get_or_404(item_id)

        db.session.delete(item)
        db.session.commit()
        return {"message":f"The item {item.name} was deleted"}


    #order of decorators matter
    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self,item_data, item_id):

        #item_data = request.get_json()

        #check to make sure it has expecte data
        # if "price" not in item_data or "name" not in item_data:
        #     abort(400, message="Bad request. Need to cinluded 'price' and 'name' ")

        #need to remove or_404 or else clause won't run
        item = ItemModel.query.get(item_id)
        if item: 
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            #if store id is not passed, this will fail
            item = ItemModel(id=item_id,**item_data)
        
        db.session.add(item)
        db.session.commit()

        return item
                    

        #This approach is not itempotent
        # item = ItemModel.query.get_or_404(item_id)

        # item.price = item_data["price"]
        # item.name = item_data["name"]

        # db.session.add(item)
        # db.session.commit()

        # return item
        # raise NotImplementedError("Updating an item is not implemented")


@blp.route("/item")
class ItemList(MethodView):

    #many = True turns dictionary into a list?
    @jwt_required()
    @blp.response(200,ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
        # return items.values()
        #list of items, not object
        #return {"items":list(items.values())}


    #2nd argument after self contains json data that has been validated by the schema

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(200, ItemSchema)
    def post(self, item_data):
        #NO LONGER NEEDED 
        #item_data = request.get_json()

        #make sure all the necessary keys are included
        #NO LONGER NEED IF STATEMENTS BECAUSE VALIDATION HANDLED BY SCHEMA
        # if (
        #     "price" not in item_data
        #     or "store_id" not in item_data
        #     or "name" not in item_data
        # ):
        #     abort(
        #         400,
        #         message="Bad request. Ensure 'price', 'store_id' and 'name' are included."
        #     )
        
        #check if item already exists
        #for item in items.values():
            #Already checkedin databas so this code is not necessary
        #    if (item_data["name"] == item["name"]
        #     and item_data["store_id"] == item["store_id"] ):
        #         abort(400, message="Item already exists")

        #turns data from client into keyword arguments that will be passed to item model
        item = ItemModel(**item_data)

        try: 
            #add to session => put it in a place where it's not wrriten in the database yet, can add multiple things if you wish
            #if there is a problem, will skip to error
            db.session.add(item)

            #commit is when it actually gets saved
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred when inserting an ite,")

        return item
