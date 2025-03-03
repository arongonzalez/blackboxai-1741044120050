from flask import Flask
from .routes import init_routes

def setup_routes(app: Flask) -> Flask:
    """Initialize all routes for the application"""
    return init_routes(app)
