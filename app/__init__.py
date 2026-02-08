import os
from flask import Flask
from pathlib import Path

from .db import init_db

def create_app():
    app = Flask(__name__)
    app.config["DATABASE"] = str(Path(app.root_path).parent / "data" / "preppulse.db")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["RESET_TOKEN_MAX_AGE"] = int(os.getenv("RESET_TOKEN_MAX_AGE", "900"))
    app.config["SMTP_HOST"] = os.getenv("SMTP_HOST", "smtp.gmail.com")
    app.config["SMTP_PORT"] = int(os.getenv("SMTP_PORT", "587"))
    app.config["SMTP_USER"] = os.getenv("SMTP_USER", "")
    app.config["SMTP_PASSWORD"] = os.getenv("SMTP_PASSWORD", "")
    app.config["SMTP_USE_TLS"] = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
    app.config["OPEN_API_KEY"] = os.getenv("OPEN_API_KEY", "")

    init_db(app)

    # Import routes
    from .routes import main
    app.register_blueprint(main)

    return app
