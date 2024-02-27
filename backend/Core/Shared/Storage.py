import firebase_admin
from firebase_admin import credentials,auth
from firebase_admin import storage
import json
import os
import uuid

db = storage.bucket()

class Storage:
    @staticmethod
    def store(file, filename):
        blob = db.blob(filename)
        blob.metadata = {"firebaseStorageDownloadTokens": str(uuid.uuid4())}
        
        blob.upload_from_file(file)
        download_url = blob.public_url
        # Create a token by default 
        blob.make_public()
        return download_url

    @staticmethod
    def delete(filename):
        blob = db.blob(filename)
        return blob.delete()
    