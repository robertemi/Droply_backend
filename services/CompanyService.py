from models.Company import Company
from typing import Optional, List, Dict
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

class CompanyService:
    @staticmethod
    def register_company(
            conn,
            name: str,
            address: str,
            password: str,
            email: str
    ) -> Optional[Company]:
        """Handles complete company registration workflow"""
        try:
            # Validate required fields
            if not all([name, address]):
                raise ValueError("Name and address are required")

            hashed_password = generate_password_hash(password)

            # Create using model's create method
            company = Company.create(
                conn=conn,
                name=name,
                address=address,
                password=hashed_password,
                email=email
            )
            return company

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Company registration failed service: {e}")
            return None
        except Exception as e:
            conn.rollback()
            print(f"Validation error: {e}")
            return None

    # to be used for log in functionality
    @staticmethod
    def get_company_from_email_and_password(
            conn, email, password
    ):
        try:
            company_id = Company.get_by_email_and_password(conn, email, password)
            return company_id
            # company = Company.get_by_email_and_password(conn, email, password)
            # return company

        except Exception as e:
            print(f"Encountered: {e}")
        finally:
            conn.rollback()

