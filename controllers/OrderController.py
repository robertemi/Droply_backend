from flask import Blueprint, request, jsonify
from services.OrderService import OrderService
from config import get_db_connection

order_bp = Blueprint('order', __name__, url_prefix='/api/orders')

@order_bp.route('', methods=['POST'])
def create_order():
    conn = get_db_connection()
    try:
        data = request.get_json()

        if not all([data.get('company_id'), data.get('pickup_address'), data.get('delivery_address')]):
            return jsonify({"error": "Missing fields required"}), 400

        order = OrderService.create_order(
            conn=conn,
            company_id=data['company_id'],
            pickup_address=data['pickup_address'],
            delivery_address=data['delivery_address'],
            courier_id=data['courier_id'] if data['courier_id'] else None
        )

        if not order:
            return jsonify({"error": "Company registration failed"}), 400

        return jsonify(order.to_dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@order_bp.route('/assign_courier', methods=['POST'])
def assign_courier():
    conn = get_db_connection()
    try:
        data = request.get_json()

        if not all([data.get('order_id'), data.get('courier_id')]):
            return jsonify({"error: Required fields missing"}), 400

        success = OrderService.assign_courier(
            conn,
            order_id=data['order_id'],
            courier_id=data['courier_id']
        )

        if not success:
            return jsonify({"error": "Courier assignment failed"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()