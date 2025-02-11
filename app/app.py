from httplib2 import Credentials
from api import create_api
from application import Application
# from scratch import firebase_login

if __name__ == '__main__':
    # Initialize the firebase application
    # cred = Credentials.Certificate('creds/firebase-cred.json')
    # firebase_login.initialize_app(cred)

    # Initialize Flask app
    app = create_api(__name__, Application())
    app.run(host="0.0.0.0", port=5000)
