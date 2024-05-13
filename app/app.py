from api import create_api
from application import Application

if __name__ == '__main__':
    app = create_api(__name__, Application())
    app.run(host="localhost", port=5000)