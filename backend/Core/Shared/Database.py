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
    def store(collection , document , query_dict):
        doc_ref = db.collection(collection).document(document)
        try:
            doc_ref.set(query_dict)
            return (0,0)
        except Exception as e:
            return (1,str(e))


    @staticmethod
    def read(collection , document):
        doc_ref = db.collection(collection).document(document)
        try:
            return (0,doc_ref.get())
        except Exception as e:
            return (1,str(e))

    @staticmethod
    def edit(collection , document,querydict):
        doc_ref = db.collection(collection).document(document)
        try:
            doc_ref.update(querydict)
            return (0, 0)
        except Exception as e:
            return (1, str(e))

    @staticmethod
    def delete(collection , document):
        event_ref = db.collection(collection).document(document)
        try:
            event_ref.delete()
            return (0, 0)
        except Exception as e:
            return (1, str(e))