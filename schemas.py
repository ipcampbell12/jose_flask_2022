from marshmallow import Schema, fields

#dump_only = True basically means this filed is read only 
#only used for returning data (e.g. sending data back to the client)
#id field won't be used for validation


#validate the types
class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name=fields.Str(required=True)
    price = fields.Float(required=True)
    

class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name=fields.Str(required=True)

class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name=fields.Str(required=True)

# for put request
# fields are NOT required because the user may not choose to update either or both fields
class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id=fields.Int()

#use marshmallow schemas to make sure data has been correclty typed

#need to use inheritance for nested fields

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(),dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()),dump_only=True)

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()),dump_only=True)
    store = fields.List(fields.Nested(PlainTagSchema()),dump_only=True)

class TagSchema(PlainTagSchema):
    store_id = fields.Int( load_only=True)
    store = fields.Nested(PlainStoreSchema(),dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()),dump_only=True)

class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)

class UserSchema(Schema):
    #dump_only because you will never recieve an id from client (read only)
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)

    #load only because you never wwant to return user's password (write only)
    password = fields.Str(required=True, load_only=True)

#only need this for when useres register, now when they log in
class UserRegisterSchema(UserSchema):
    email = fields.Str(required=True)