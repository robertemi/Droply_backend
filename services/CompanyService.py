from models.Company import Company
from typing import Optional, List, Dict
import psycopg2


class CompanyService:
    @staticmethod
    def register_company(
            conn,
            name: str,
            address: str,
            password: str
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
                password=password
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
