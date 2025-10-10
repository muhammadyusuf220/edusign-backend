import firebase_admin
from firebase_admin import credentials, storage, firestore

cred = credentials.Certificate("edusign-433e2-firebase-adminsdk-fbsvc-e5d7bb91aa.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'edusign-433e2.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()
