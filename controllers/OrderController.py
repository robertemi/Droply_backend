from flask import Blueprint, request, jsonify
from services.OrderService import OrderService
from config import get_db_connection

order_bp = Blueprint('order', __name__, url_prefix='/api/orders')

@order_bp.route('', methods=['POST'])
def create_order():
    conn = get_db_connection()
    try:
        data = request.get_json()
        print(f"Received Data: {data}")

        if not all([data.get('pickup_address'), data.get('delivery_address')]):
            return jsonify({"error": "Missing fields required"}), 400

        courier_id = data.get('courier_id')

        print(f"Attempt to create Order: {data['pickup_address']}, {data['delivery_address']}")
        order = OrderService.create_order(
            conn=conn,
            company_id=data['company_id'],
            pickup_address=data['pickup_address'],
            delivery_address=data['delivery_address']
        )

        if not order:
            print(f"Order Service returned None")
            return jsonify({"error": "Company registration failed"}), 400

        return jsonify(order.to_dict()), 201


    except Exception as e:
        print(f"Order creation failed: {e}")  # <--- Add this line
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()


@order_bp.route('/unassigned', methods=['GET'])
def get_unassigned_orders():
    conn = get_db_connection()
    try:
        orders = OrderService.get_unassigned_order(conn)
        if not orders:
            return jsonify([]), 200

        return jsonify([order.to_dict() for order in orders]), 200

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

        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@order_bp.route('/available_orders', methods=['GET'])
def get_company_orders():
    conn = get_db_connection()
    company_id = request.args.get('company_id')
    if not company_id:
        return {'error': 'Missing company_id'}, 400
    try:
        orders = OrderService.get_company_orders(conn, company_id)
        return jsonify({'orders': orders}), 200
    except Exception as e:
        print(f"Error in get_company_orders: {e}")
        return {'error': str(e)}, 500
    finally:
        conn.close()

@order_bp.route('/delete_order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = get_db_connection()
    try:
        OrderService.delete_order(conn, order_id)
        conn.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error in delete_order: {e}")
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
        
@order_bp.route('/track/<string:awb>', methods=['GET', 'OPTIONS'])
def track_package(awb):
    """Track package by AWB number"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,Accept,Origin,X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET,OPTIONS")
        return response
    
    print(f"Tracking request for AWB: '{awb}'")
    conn = get_db_connection()
    try:
        # Add debugging to see what's in the database
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM orders")
            total_orders = cur.fetchone()[0]
            print(f"Total orders in database: {total_orders}")
            
            cur.execute("SELECT COUNT(*) FROM orders WHERE awb IS NOT NULL")
            orders_with_awb = cur.fetchone()[0]
            print(f"Orders with AWB: {orders_with_awb}")
            
            cur.execute("SELECT awb FROM orders WHERE awb IS NOT NULL LIMIT 5")
            sample_awbs = cur.fetchall()
            print(f"Sample AWBs in database: {[row[0] for row in sample_awbs]}")
            
            # Check for exact match
            cur.execute("SELECT COUNT(*) FROM orders WHERE awb = %s", (awb,))
            exact_match = cur.fetchone()[0]
            print(f"Exact match for '{awb}': {exact_match}")
            
            # Check for case-insensitive match
            cur.execute("SELECT COUNT(*) FROM orders WHERE LOWER(awb) = LOWER(%s)", (awb,))
            case_insensitive_match = cur.fetchone()[0]
            print(f"Case-insensitive match for '{awb}': {case_insensitive_match}")
        
        tracking_info = OrderService.get_tracking_info(conn, awb)
        
        if not tracking_info:
            print(f"No tracking info found for AWB: '{awb}'")
            response = jsonify({"error": "Tracking number not found"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 404
        
        print(f"Successfully found tracking info for AWB: '{awb}'")
        response = jsonify(tracking_info)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200
        
    except Exception as e:
        print(f"Error tracking package: {e}")
        response = jsonify({"error": "Internal server error"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500
    finally:
        conn.close()