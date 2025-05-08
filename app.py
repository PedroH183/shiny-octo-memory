from flask import Flask
from routers import bp as router_app

app = Flask("MyMinimalApp")
app.register_blueprint(router_app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
