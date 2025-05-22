import psycopg2


class Courier():
    def __init__(self, courier_id: int, name: str, vehicle_type: str, rating: int, balance: float, password: str, email: str):
        self.courier_id = courier_id
        self.name = name
        self.vehicle_type = vehicle_type
        self.rating = rating
        self.balance = balance
        self.password = password
        self.email = email

    @classmethod
    def create(cls, conn, name: str, vehicle_type: str, rating: int, balance: float, password: str, email: str):
        """Create new courier in database"""
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO couriers (name, vehicle_type, rating, balance, password, courier_email) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING courier_id",
                    (name, vehicle_type, rating, balance, password, email)
                )
                courier_id = cur.fetchone()[0]
                conn.commit()
                return cls(courier_id, name, vehicle_type, rating, balance, password, email)
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Courier creation failed: {e}")
            return None

    @classmethod
    def get_by_id(cls, conn, id: int):
        """Retrieve courier by id"""
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM couriers WHERE courier_id = %s",
                (id,)
            )
            result = cur.fetchone()
            if result:
                return cls(
                    courier_id=result[0],
                    name=result[1],
                    vehicle_type=result[2],
                    rating=result[3],
                    balance=result[4],
                    password=result[5],
                    email=result[6]
                )
            return None

    @classmethod
    def get_by_email_and_password(cls, conn, email: str, password: str):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM couriers WHERE courier_email = %s AND password = %s",
                    (email, password)
                )
                result = cur.fetchone()
                if result:
                    return cls(
                        courier_id=result[0],
                        name=result[1],
                        vehicle_type=result[2],
                        rating=result[3],
                        balance=result[4],
                        password=result[5],
                        email=result[6]
                    )
        except Exception as e:
            print(f"Encountered error: {e}")

    def to_dict(self) -> dict:
        """Convert to API-friendly format"""
        return {
            'courier_id': self.courier_id,
            'name': self.name,
            'vehicle_type': self.vehicle_type,
            'rating': float(self.rating),
            'balance': float(self.balance),
            'courier_email': self.email
        }