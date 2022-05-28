from flask import Flask, jsonify, request,json
from flask_pymongo import PyMongo
from marshmallow import Schema,fields, ValidationError
app = Flask(__name__)
from dotenv import load_dotenv
from bson.json_util import dumps
from json import loads
import os
import datetime

load_dotenv()

app.config["MONGO_URI"]=os.getenv("MONGO_CONNECTION_STRING")
mongo = PyMongo(app)
class TankSchema(Schema):
        location = fields.String(required=True)
        latitude = fields.Float(required=True)
        longitude = fields.Float(required=True)
        percentage_full = fields.Integer(required=True)
user={}

@app.route('/', methods=['GET'])

@app.route('/profile',  methods=["GET", "POST","PATCH"])
def account():
  if request.method == "POST":
    global user

    time=datetime.datetime.now()
    user = {
        "last_updated":time,
        "username":request.json["username"],
        "purpose":request.json["purpose"],
        "color":request.json["color"]
    }
    return {"data":user}
  elif request.method == "GET":
    return user
  elif request.method == "PATCH":
    if "username" in request.json:
      user["username"] = request.json["username"]

    if "purpose" in request.json:
      user["purpose"] = request.json["purpose"]

    if "color" in request.json:
      user["color"] = request.json["color"]

    time = datetime.datetime.now()

    return {
      "data": user
    }

@app.route('/data', methods=["GET","POST"])
def data():
  if request.method == "GET":
        tanks = mongo.db.tanks.find()
        return jsonify(loads(dumps(tanks)))
  if request.method == "POST":
      try:
        newtank=TankSchema().load(request.json)
        tank_id = mongo.db.tanks.insert_one(newtank).inserted_id
        tank = mongo.db.tanks.find_one(tank_id)
        return loads(dumps(tank))
      except ValidationError as error:
        return error.messages, 400

@app.route('/data/<ObjectId:id>', methods=["DELETE"])
def deletank(id):
    result = mongo.db.tanks.delete_one({"_id": id})
    if result.deleted_count == 1:
        return {
      "success": True
    }
    else:
        return {
      "success": False
    }, 400

@app.route('/data/<ObjectId:id>', methods=["PATCH"])
def datapatch(id):
    mongo.db.tanks.update_one({"_id":id},{"$set":request.data})
    tank = mongo.db.tanks.find_one(id)
    return loads(dumps(tank))

if __name__ =="__main__":
    app.run(debug=True,
    port=3000,
    host="0.0.0.0")