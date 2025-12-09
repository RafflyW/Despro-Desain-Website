from flask import Flask
import logging

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'kelompok13'

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Register blueprints
    from .views import views
    from .esp32_routes import esp32_bp
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(esp32_bp)
    
    return app