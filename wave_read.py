import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc_ref = db.document("人選之人─造浪者/7gsSjURW8T6X0i5cRGc7")
doc = doc_ref.get()
result = doc.to_dict()
print(result)
print(result["name"])
print(result["birth"])