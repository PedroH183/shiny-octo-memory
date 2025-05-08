import logging
from flask import Blueprint, jsonify, request
from database import AccessLogsDatabase, ProductsDatabase

logger = logging.getLogger("input")

bp = Blueprint("router", __name__)

@bp.route("/")
def index():
    return jsonify({"text": "I'm Alive...."}), 200


@bp.route("/products", methods=["POST"])
def products():
    """Create a new product"""
    data = request.get_json()
    logger.info(f"0o0o0o0o0o0o0 Received data: {data} 0o0o0o0o0o0")
    return ProductsDatabase().put_item(data)


@bp.route("/products/<int:product_id>", methods=["GET"])
def product(product_id):
    """Get a product by ID"""
    logger.info(f"0o0o0o0o0o0o0 Getting product with ID: {product_id} 0o0o0o0o0o0")
    return ProductsDatabase().get_item(product_id)


@bp.route("/logs")
def logs():
    """Get access logs"""
    logger.info("0o0o0o0o0o0o0 Getting access logs 0o0o0o0o0o0")
    return AccessLogsDatabase().get_logs()
