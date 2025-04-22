from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from config import Config

# Initialize extensions
mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mongo.init_app(app)
    login_manager.init_app(app)

    # Add custom filter for number formatting
    @app.template_filter('format_number')
    def format_number(value):
        return f"{int(value):,}"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.get_by_id(user_id)

    # Register blueprints
    from app.exam import exam_bp
    from app.auth import auth_bp
    app.register_blueprint(exam_bp, url_prefix='/exam')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Import and initialize routes after app is fully configured
    from app import routes
    app = routes.create_routes(app)
    return app