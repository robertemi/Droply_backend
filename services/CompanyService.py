from models.Company import Company
from typing import Optional, List, Dict
import psycopg2


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

            # Create using model's create method
            company = Company.create(
                conn=conn,
                name=name,
                address=address,
                password=password,
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

    @staticmethod
    def get_company_orders(conn, company_id):
        try:
            orders = Company.get_company_orders(conn, company_id)
            return orders
        except Exception as e:
            return print(f"Unexpected")


    # to be used for log in functionality
    @staticmethod
    def get_company_from_email_and_password(
            conn, email, password
    ):
        try:
            company = Company.get_by_email_and_password(conn, email, password)
            return company

        except Exception as e:
            print(f"Encountered: {e}")
        finally:
            conn.rollback()

