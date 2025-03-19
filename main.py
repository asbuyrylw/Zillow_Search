from flask import Flask
import os
import logging
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from routes import routes
from billing_routes import billing_routes
from tasks import celery
import os
print("FLASK_ENV:", os.getenv("FLASK_ENV"))
print("STRIPE_SECRET_KEY:", os.getenv("STRIPE_SECRET_KEY"))
print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))
print("SCRAPEAK_API_KEY:", os.getenv("SCRAPEAK_API_KEY"))
print("GOOGLE_CX_ID:", os.getenv("GOOGLE_CX_ID"))
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
print("AWS_REGION:", os.getenv("AWS_REGION"))
print("DYNAMODB_TABLE:", os.getenv("DYNAMODB_TABLE"))
print("CELERY_BROKER_URL:", os.getenv("CELERY_BROKER_URL"))
print("REDIS_URL:", os.getenv("REDIS_URL"))
print("AWS_SECRET_MANAGER:", os.getenv("AWS_SECRET_MANAGER"))

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
