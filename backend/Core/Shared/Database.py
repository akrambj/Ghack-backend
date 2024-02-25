import firebase_admin
from firebase_admin import credentials,auth
from firebase_admin import firestore
import json
import os

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "../firebase.json")

cred = credentials.Certificate(CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

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