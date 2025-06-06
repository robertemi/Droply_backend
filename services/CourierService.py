from models.Courier import Courier
from models.Order import Order
from werkzeug.security import generate_password_hash
class CourierService:
    @staticmethod
    def create_courier(
        conn, name, vehicle_type, password, email
    ):
        try:
            hashed_password = generate_password_hash(password)

            courier = Courier.create(
                conn=conn,
                name=name,
                vehicle_type=vehicle_type,
                password=hashed_password,
                email=email
            )
            return courier.courier_id
        except Exception as e:
            conn.rollback()
            print(f"Courier creation failed: {str(e)}")
            return None

    @staticmethod
    def get_courier_from_email_and_password(
            conn, email, password
    ):
        try:
            courier_id = Courier.get_by_email_and_password(conn, email, password)
            return courier_id

        except Exception as e:
            print(f"Encountered: {e}")
        finally:
            conn.rollback()



    # @staticmethod
    # def assign_order(conn, courier_id, order_id):
    #     courier = Courier.get_by_id(conn, courier_id)
    #     if not courier or not courier.is_available:
    #         return False
    #
    #     # 2. Use model's basic update
    #     return Order.update_courier(
    #         conn=conn,
    #         order_id=order_id,
    #         courier_id=courier_id
    #     )