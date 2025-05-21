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

        # Required fields
        if not all([data.get('name'), data.get('address')]):
            return jsonify({"error": "Name and address are required"}), 400

        # Create company
        company = CompanyService.register_company(
            conn=conn,
            name=data['name'],
            address=data['address']
        )

        if not company:
            return jsonify({"error": "Company registration failed"}), 400

        return jsonify(company.to_dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

