from api import create_api
from application import Application

if __name__ == '__main__':
    app = create_api(__name__, Application())
    app.run(host="0.0.0.0", port=5000)
