import psycopg2


class Company():
    def __init__(self, company_id, name, address, password):
        self.company_id = company_id
        self.name = name
        self.address = address
        self.password = password

    @classmethod
    def create(cls, conn, name, address, password):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO companies (name, address, password) "
                    "VALUES (%s, %s, %s) RETURNING company_id",
                    (name, address, password)
                )
                company_id = cur.fetchone()[0]
                conn.commit()
                return cls(company_id, name, address, password)
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Company creation failed: {e}")
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
                    password=result[3]
                )
            return None

    def to_dict(self) -> dict:
        """Convert to API-friendly format"""
        return {
            'company_id': self.company_id,
            'name': self.name,
            'address': self.address
        }
