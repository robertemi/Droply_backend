from flask import Blueprint, request, jsonify
from services.OrderStatusHistoryService import OrderStatusHistoryService
from config import get_db_connection

order_status_history_bp = Blueprint('order_status_history', __name__, url_prefix='/api/order_status_history')

@order_status_history_bp.route('', methods=['POST'])
def create_order_status_history():
    conn = get_db_connection()
    try:
        data = request.get_json()
        print(f"Received data: {data}")

        if not all([data.get('order_id'), data.get('status')]):
            return jsonify({"error": "Missing fields required"}), 400

        print(f"Attempt to create OrderStatusHistory: {data['order_id']}, {data['status']}")
        order_status_history = OrderStatusHistoryService.create(
            conn=conn,
            order_id=data['order_id'],
            new_status=data['status'],
        )

        if not order_status_history:
            print(f"OrderStatusHistory Service returned None")
            return jsonify({"error": "Order status history creation failed"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@order_status_history_bp.route('/status_change', methods=['POST'])
def record_status_change():
    conn = get_db_connection()
    try:
        data = request.get_json()

        if not all([data.get('order_id'), data.get('new_status')]):
            return jsonify({"error": "Missing fields required"}), 400

        success = OrderStatusHistoryService.record_status_change(
            conn=conn,
            order_id=data['order_id'],
            new_status=data['new_status']
        )

        if not success:
            return jsonify({"error": "Order status history change failed"}), 400

        return jsonify({"message": "Order status updated successfully"}), 200

    except Exception as e:
        conn.rolback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()