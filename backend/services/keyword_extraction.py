from keybert import KeyBERT
import tika
from tika import parser
import filetype
import sys
import json

import requests
import os

UserName="AZIZAISSA"
LicenseCode="F1DEF76B-F860-4E22-BCF9-AB01A85C654A"

RequestUrl = "http://www.ocrwebservice.com/restservices/processDocument?gettext=true";



def extract_text_from_file(filepath):
      # exctract text from file

        kind = filetype.guess(filepath)
        
        if kind is None:
            return None
        if kind.mime in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'application/msword'] : 
            # from pdf, doxc, txt  
            tika.initVM()
            parsed = parser.from_file(filepath)
            print(parsed["metadata"])
            print(parsed["content"])
            return parsed["content"]
        elif kind.mime in ['image/png', 'image/jpeg', 'image/gif'] : 
            # from images 
            with open(filepath, 'rb') as image_file:
                image_data = image_file.read()
    
            r = requests.post(RequestUrl, data=image_data, auth=(UserName, LicenseCode))

            if r.status_code == 401:
                print("Unauthorized request")
                return None

            # Decode Output response
            jobj = json.loads(r.content)
            ocrError = str(jobj["ErrorMessage"])
            
            if ocrError != '':
            #Error occurs during recognition
                print ("Recognition Error: " + ocrError)
                return None
            
            return str(jobj["OCRText"][0][0])
        else: 
            return None
        

def exctract_keyword(filepath):
    try: 
      
        doc = extract_text_from_file(filepath)

        if doc is None: 
            return None
        
        kw_model = KeyBERT()
        
        list =  kw_model.extract_keywords(doc,keyphrase_ngram_range=(3, 3), stop_words='english',
                                  use_maxsum=True, diversity=0.7)
        print(list)
        
        return [item[0] for item in list ]
    except: 
        return None