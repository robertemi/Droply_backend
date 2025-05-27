import psycopg2


class Company():
    def __init__(self, company_id, name, address, password, email):
        self.company_id = company_id
        self.name = name
        self.address = address
        self.password = password
        self.email = email

    @classmethod
    def create(cls, conn, name, address, password, email):
        try:
            with conn.cursor() as cur:
                print(f"Attempting to insert: {name}, {address}, {password}, {email}")  # Debug log
                cur.execute(
                    "INSERT INTO companies (name, address, password, company_email) "
                    "VALUES (%s, %s, %s, %s) RETURNING company_id",
                    (name, address, password, email)
                )
                result = cur.fetchone()
                if not result:
                    print("No ID returned from INSERT")  # Debug log
                    return None

                company_id = result[0]
                conn.commit()
                print(f"Successfully created company ID: {company_id}")  # Debug log
                return cls(company_id, name, address, password, email)
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error in Company.create(): {e.pgerror}")  # Show full error
            print(f"Database error code: {e.pgcode}")  # Show error code
            return None


    @classmethod
    def get_by_id(cls, conn, id: int):
        """Retrieve company by id"""
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM companies WHERE company_id = %s",
                (id,)
            )
            result = cur.fetchone()
            if result:
                return cls(
                    company_id=result[0],
                    name=result[1],
                    address=result[2],
                    password=result[3],
                    email=result[4]
                )
            return None

    @classmethod
    def get_by_email_and_password(cls, conn, email: str, password: str):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM companies WHERE company_email = %s AND password = %s",
                    (email, password)
                )
                result = cur.fetchone()
                if result:
                    return cls(
                        company_id=result[0],
                        name=result[1],
                        address=result[2],
                        password=result[3],
                        email=result[4]
                    )
        except Exception as e:
            print(f"Encountered error: {e}")

    def to_dict(self) -> dict:
        """Convert to API-friendly format"""
        return {
            'company_id': self.company_id,
            'name': self.name,
            'address': self.address,
            'company_email': self.email
        }
