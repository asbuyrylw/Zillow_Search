from flask import Flask
import os
import logging
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from routes import routes
from billing_routes import billing_routes
from tasks import celery

# ✅ Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app)
app.register_blueprint(routes)
app.register_blueprint(billing_routes)
app.register_blueprint(auth_routes)

# ✅ JWT Authentication
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")
jwt = JWTManager(app)

# ✅ AWS X-Ray for Performance Monitoring
from aws_xray_sdk.core import xray_recorder, patch_all
xray_recorder.configure(service="RealtyEnrichAPI")
patch_all()

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
