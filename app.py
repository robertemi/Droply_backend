from flask import Flask, jsonify
from config import Config
import logging
from flask import Flask
from flask_cors import CORS

from controllers import (
    CompanyController,
    CourierController,
    OrderController,
    OrderStatusHistoryController
)

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configure CORS properly for production
    # CORS(app,
    #      origins=['*'],  # Allow all origins - can be restricted later
    #      methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    #      allow_headers=['Content-Type', 'Authorization', 'Accept', 'Origin', 'X-Requested-With'],
    #      supports_credentials=False)  # Set to False for wildcard origins

    CORS(app,
         resources={r"/*": {"origins": "*"}},
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization', 'Accept', 'Origin', 'X-Requested-With'],
         supports_credentials=False)
    
    app.config.from_object(config_class)

    # # Setup logging
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # )
    # logger = logging.getLogger(__name__)    # Register blueprints
    app.register_blueprint(CompanyController.company_bp)
    app.register_blueprint(CourierController.courier_bp)
    app.register_blueprint(OrderController.order_bp)
    app.register_blueprint(OrderStatusHistoryController.order_status_history_bp)

    # Add CORS headers to all responses
    # @app.after_request
    # def after_request(response):
    #     response.headers.add('Access-Control-Allow-Origin', '*')
    #     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin,X-Requested-With')
    #     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    #     return response

    # Health check endpoint
    @app.route('/')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'services': ['companies', 'couriers', 'orders', 'status-history'],
            'cors': 'enabled'
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', False)
    )