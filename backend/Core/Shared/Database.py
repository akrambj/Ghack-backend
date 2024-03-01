import firebase_admin
from firebase_admin import credentials,auth
from firebase_admin import firestore
from Core.env import *
import json
import os

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "../firebase.json")

cred = credentials.Certificate(CREDENTIALS_PATH)
firebase_admin.initialize_app(cred,{
        'storageBucket': STORAGE_BUCKET
    })

db = firestore.client()

class Database:
    @staticmethod
    def store(collection , document , dict):
        doc_ref = db.collection(collection).document(document)
        return doc_ref.set(dict)


    @staticmethod
    def read(collection , document):
        doc_ref = db.collection(collection).document(document)
        if doc_ref.get().exists:
            return doc_ref.get().to_dict()
        else:
            return None
 

    @staticmethod
    def edit(collection , document,querydict):
        doc_ref = db.collection(collection).document(document)
        return  doc_ref.update(querydict)


    @staticmethod
    def delete(collection , document):
        event_ref = db.collection(collection).document(document)
        return event_ref.delete()
    
    @staticmethod
    def exists(collection,document):
        doc_ref = db.collection(collection).document(document)
        return doc_ref.get().exists

    @staticmethod
    def userByEmail(email):
        result = db.collection("users").where("email", "==", email.lower()).get()
        if len(result) == 0:
            return None
        return result[0].to_dict()