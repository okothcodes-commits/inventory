from typing import Optional

from flask import Flask

from .errors import register_error_handlers
from .routes import bp
from .store import InventoryStore


def create_app(store: Optional[InventoryStore] = None) -> Flask:
    """Build a Flask app. Passing in a store makes testing easy."""
    app = Flask(__name__)
    app.extensions["inventory_store"] = store if store is not None else InventoryStore()
    app.register_blueprint(bp)
    register_error_handlers(app)
    return app
