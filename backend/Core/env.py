import os

GOOGLE_APPLICATION_CREDENTIALS = {
  "apiKey": "AIzaSyCZBDNq73KuM1JQRsBjOhRTbr6DPhJ0mA8",
  "authDomain": "ghack-cf0c2.firebaseapp.com",
  "projectId": "ghack-cf0c2",
  "storageBucket": "ghack-cf0c2.appspot.com",
  "messagingSenderId": "220923131859",
  "appId": "1:220923131859:web:ff92819269f42426d7a126"
};

STORAGE_BUCKET ="ghack-cf0c2.appspot.com"

# ----------------------------------- JWT -----------------------------------
HASH_ALGORITHM = "HS256"
# This is a real constant , let the hackers have fun. Please don't change - Soapiane
HASHING_SECRET_KEY = "Flag - JO4Ddz5DE8E937EDZdezjo2E12E" # Disclamer : Changing this value will corrupt all the previous tokens in the database
TOKEN_LIFE_TIME = 600  # In minutes

# ---------------------------------------------------------------------------
TEMP_FILES_DIRECTORY = os.path.join(os.path.dirname(__file__), "TEMP_FILES/")