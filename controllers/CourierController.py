from flask import Blueprint, request, jsonify
from services.CourierService import CourierService
from config import get_db_connection

courier_bp = Blueprint('courier', __name__, url_prefix='/api/couriers')

@courier_bp.route('', methods=['POST'])
def create_courier():
    conn = get_db_connection()
    try:
        data = request.get_json()
        print(f"Received data: {data}")

        if not all([data.get('name'), data.get('vehicle_type'), data.get('courier_email')]):
            return jsonify({"error": "Missing fields required"}), 400

        print(f"Attempt to create Courier: {data['name']}, {data['vehicle_type']}, {data['courier_email']}")
        courier = CourierService.create_courier(
            conn,
            name=data['name'],
            vehicle_type=data['vehicle_type'],
            password=data['password'],
            email=data['courier_email']
        )

        if not courier:
            print(f"CourierService returned None")
            return jsonify({"error": "Courier creation failed"}), 400

        return jsonify(courier.to_dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@courier_bp.route('/log_in', methods=['POST'])
def validate_log_in():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"})

        conn = get_db_connection()
        courier = CourierService.get_courier_from_email_and_password(
            conn, data['courier_email'], data['password']
        )

        if courier:
            return jsonify({
                "success": True,
                "company": courier.to_dict()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Invalid credentials"
            }), 401

    except Exception as e:
        print(f"Encountered: {e}")
    finally:
        if conn:
            conn.close()