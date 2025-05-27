from flask import Blueprint, request, jsonify
from services.CompanyService import CompanyService
from config import get_db_connection

company_bp = Blueprint('company', __name__, url_prefix='/api/companies')


@company_bp.route('', methods=['POST'])
def register_company():
    """Register a new company"""
    conn = get_db_connection()
    try:
        data = request.get_json()
        print(f"Received data: {data}")

        # Required fields - now including password
        if not all([data.get('name'), data.get('address'), data.get('password'), data.get('company_email')]):
            print("Missing required fields")
            return jsonify({"error": "Name, address, and password are required"}), 400

        print(f"Attempting to create company: {data['name']}, {data['address']}, {data['company_email']}")
        company = CompanyService.register_company(
            conn=conn,
            name=data['name'],
            address=data['address'],
            password=data['password'],
            email=data['company_email']
        )

        if not company:
            # Get the last database error
            with conn.cursor() as cur:
                cur.execute("SHOW server_version;")
                print("PostgreSQL version:", cur.fetchone())
            return jsonify({"error": "Database operation failed - check logs controller"}), 400

        return jsonify(company.to_dict()), 201
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

'''
If the company, given email and password is found, the user can proceed as company, else try again
'''

@company_bp.route('/log_in', methods=['POST'])
def validate_log_in():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"})

        conn = get_db_connection()
        company = CompanyService.get_company_from_email_and_password(
            conn, data['company_email'], data['password']
        )

        if company:
            return jsonify({
                "success": True,
                "company": company.to_dict()
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

@company_bp.route('/available_orders', methods=['GET'])
def get_company_orders():
    conn = get_db_connection()
    company_id = request.args.get('company_id')
    if not company_id:
        return {'error': 'Missing company_id'}, 400
    try:
        orders = CompanyService.get_company_orders(conn, company_id)
        return jsonify({'orders': orders}), 200
    except Exception as e:
        return {'error': str(e)}, 500