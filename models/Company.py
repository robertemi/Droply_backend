import psycopg2


class Company():
    def __init__(self, company_id, name, address):
        self.company_id = company_id
        self.name = name
        self.address = address

    @classmethod
    def create(cls, conn, name, address):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO companies (name, address) "
                    "VALUES (%s, %s) RETURNING company_id",
                    (name, address)
                )
                company_id = cur.fetchone()[0]
                conn.commit()
                return cls(company_id, name, address)
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Company creation failed: {e}")
            return None

    @classmethod
    def get_by_id(cls, conn, id: int):
        """Retrieve company by id"""
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM companies WHERE id = %s",
                (id,)
            )
            result = cur.fetchone()
            if result:
                return cls(
                    company_id=result[0],
                    name=result[1],
                    address=result[2]
                )
            return None

    def to_dict(self) -> dict:
        """Convert to API-friendly format"""
        return {
            'company_id': self.company_id,
            'name': self.name,
            'address': self.address
        }
