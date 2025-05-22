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

        if not all([data.get('name'), data.get('vehicle_type'), data.get('rating'), data.get('balance'), data.get('email')]):
            return jsonify({"error": "Missing fields required"}), 400

        print(f"Attempt to create Courier: {data['name']}, {data['vehicle_type']}, {data['rating']}, {data['balance']}, {data['email']}")
        courier = CourierService.create_courier(
            conn,
            name=data['name'],
            vehicle_type=data['vehicle_type'],
            rating=data['rating'],
            balance=data['balance'],
            password=data['password'],
            email=data['email']
        )

        if not courier:
            print(f"CourierService returned None")
            return jsonify({"error": "Courier creation failed"}), 400

        return jsonify(courier.to_dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()