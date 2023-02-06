from db import db


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),unique=False, nullable=False)

    #the other end of the relationship with item
    #needs to find all the items with store_id equal to this store's id
    tags = db.relationship("TagModel", back_populates="store",lazy="dynamic", cascade="all,delete")
    items = db.relationship("ItemModel", back_populates="store",lazy="dynamic", cascade="all,delete")
  

    #lazy=dynamic items will not be fetched from database until it is told to
    #allows it a little faster, make request later