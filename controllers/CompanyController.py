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
        if not all([data.get('name'), data.get('address'), data.get('password'), data.get('email')]):
            print("Missing required fields")
            return jsonify({"error": "Name, address, and password are required"}), 400

        print(f"Attempting to create company: {data['name']}, {data['address']}, {data['email']}")
        company = CompanyService.register_company(
            conn=conn,
            name=data['name'],
            address=data['address'],
            password=data['password'],
            email=data['email']
        )

        if not company:
            # Get the last database error
            with conn.cursor() as cur:
                cur.execute("SHOW server_version;")
                print("PostgreSQL version:", cur.fetchone())
            return jsonify({"error": "Database operation failed - check logs"}), 400

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
def validate_log_in() -> bool:
    conn = get_db_connection()
    try:
        data = request.get_json()

        company = CompanyService.get_company_from_email_and_password(
            conn, data['company_email'], data['password']
        )

        if not company:
            return False
        return True
    except Exception as e:
        print(f"Encountered: {e}")
    finally:
        conn.close()