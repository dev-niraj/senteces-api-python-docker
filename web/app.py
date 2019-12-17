#!/usr/bin/python3

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt


app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentanceDatabase
users = db["Users"]


class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        hashed_passwd = bcrypt.hashpw(
            password.encode("utf8"), bcrypt.gensalt())

        users.insert_one({
            "Username": username,
            "Password": hashed_passwd,
            "Sentence": "",
            "Tokens": 6
        })

        retJSON = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }

        return jsonify(retJSON)


def verifyPw(username, password):
    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def countTokens(username):
    tokens = users.find({
        "Username": username
    })[0]["Tokens"]
    return tokens


class Store(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentance"]

        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJSON = {
                "status": 302
            }
            return jsonify(retJSON)

        token_left = countTokens(username)

        if token_left <= 0:
            retJSON = {
                "status": 301
            }
            return jsonify(retJSON)

        users.update({
            "Username":username
        }, {
            "$set":{
                "Sentence":sentence,
                "Tokens":token_left-1
                }
        })

        retuJson = {
            "status": 200,
            "msg": "Sentence Saved Successfully"
        }
        return jsonify(retuJson)

class Get(Resource):
    def get(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJSON = {
                "status": 302
            }
            return jsonify(retJSON)
        
        token_left = countTokens(username)

        if token_left <= 0:
            retJSON = {
                "status": 301
            }
            return jsonify(retJSON)
        
        sentence = users.find({
            "Username": username
        })[0]["Sentence"]

        retJson = {
            "status": 200,
            "message": sentence
        }

        return jsonify(retJson)


api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
