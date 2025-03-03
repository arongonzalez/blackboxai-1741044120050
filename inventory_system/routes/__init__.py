from flask import Flask
from .auth_routes import init_auth_routes
from .staff_routes import init_staff_routes
from .inventory_routes import init_inventory_routes
from .product_routes import init_product_routes
from .report_routes import init_report_routes
from .pos_routes import init_pos_routes
from .waste_routes import init_waste_routes
from .config_routes_new import init_config_routes
from .warehouse_routes import init_warehouse_routes

def init_routes(app: Flask) -> Flask:
    """Initialize all route modules"""
    app = init_auth_routes(app)
    app = init_staff_routes(app)
    app = init_inventory_routes(app)
    app = init_product_routes(app)
    app = init_report_routes(app)
    app = init_pos_routes(app)
    app = init_waste_routes(app)
    app = init_config_routes(app)
    app = init_warehouse_routes(app)
    return app

# Export the setup_routes function
setup_routes = init_routes
