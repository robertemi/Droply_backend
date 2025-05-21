from models.OrderStatusHistory import OrderStatusHistory
import datetime
class OrderStatusHistoryService:

    @classmethod
    def create(cls, conn, order_id, new_status):
        try:
            orderStatusHistory = OrderStatusHistory.create(
                conn=conn,
                order_id=order_id,
                status=new_status,
                timestamp=datetime.datetime.now()
            )
            return orderStatusHistory
        except Exception as e:
            conn.rollback()
            print(f"OrderStatusHistory creation failed: {str(e)}")
            return None


    @staticmethod
    def record_status_change(conn, order_id, new_status):
        """Business logic around status changes"""

        return OrderStatusHistory.create(
            conn=conn,
            order_id=order_id,
            status=new_status,
            timestamp=datetime.datetime.now()
        )