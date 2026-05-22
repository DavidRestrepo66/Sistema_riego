from flask import Flask

from config import Config

from routes.auth_routes import (
    auth_bp
)

from routes.sensor_routes import (
    sensor_bp
)

from routes.view_routes import (
    views_bp
)

from routes.sql_routes import (
    sql_bp
)

app = Flask(__name__)

app.secret_key = Config.SECRET_KEY

app.register_blueprint(auth_bp)

app.register_blueprint(sensor_bp)

app.register_blueprint(views_bp)

app.register_blueprint(sql_bp)

if __name__ == "__main__":

    app.run(debug=True)