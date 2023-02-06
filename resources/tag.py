from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError


from db import db
from schemas import TagSchema, TagAndItemSchema
from models import TagModel, StoreModel, ItemModel

blp = Blueprint("Tags",__name__,description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):

    #list of tags for that store
    @blp.response(200,TagSchema(many=True))
    def get(self,store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()


    #create a new tag for a particular store
    @blp.arguments(TagSchema)
    @blp.response(200,TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data,store_id=store_id)

        try: 
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:

            #turns exception into string
            abort(500, message=str(e))

        return tag

@blp.route('/tag')
class AllTags(MethodView):
    @blp.response(200,TagSchema(many=True))
    def get(self):
        tags = TagModel.query.all()

        return tags



@blp.route("/item/<int:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):


    #this doesn't create a tag or an item; just links a tag to an item
    @blp.response(201,TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        #treat tags as a list
        item.tags.append(tag)

        try:
            
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred when inserting the tag")

        return tag

    #unlink a tag from an item
    @blp.response(200,TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        #treat tags as a list
        item.tags.remove(tag)

        try:
            
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred when unlinking the tag")

        return {"message":"Item removed from tag","item":item, "tag":tag}


    

    

@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):

    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        return tag
    
    #multiple decorators
    @blp.response(
        202, 
        description="Deletes a tag if no item is tagged with it",
        example={"message":"Tag Deleted."} )
    @blp.alt_response(
        404, 
        description="Tag no found")
    @blp.alt_response(
        400, 
        description="Return if the tag is assigned to one or more items. In this case, the tag is not deleted")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        # if there are no items linked to that tag
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message":"Tag deleted."}
        abort(
            400,
            message="Could not delete tag. Make sure tag is not associated with any items, then try again."
        )


