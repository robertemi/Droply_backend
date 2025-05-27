import datetime

import psycopg2


'''
Serves to model the use case of a courier choosing an order

ONLY TO BE USED FOR INSERTING ASSGINED ORDERS

'''
class OrderStatusHistory:
    def __init__(self, order_status_history_id, order_id, status, timestamp, courier_id):
        self.order_status_history_id = order_status_history_id
        self.order_id = order_id
        self.status = status
        self.timestamp = timestamp
        self.courier_id = courier_id

    @classmethod
    def create(cls, conn, order_id, status, timestamp, courier_id):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO orderstatushistory (order_id, status, timestamp, courier_id) "
                    "VALUES (%s, %s, %s, %s) RETURNING orderstatushistory_id",
                    (order_id, status, timestamp, courier_id)
                )
                orderstatushistory_id = cur.fetchone()[0]
                conn.commit()
                return cls(orderstatushistory_id, order_id, status, timestamp)
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Order Status History creation failed: {e}")
            return None

    @classmethod
    def get_by_id(cls, conn, id: int):
        """Retrieve order status history by id"""
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM orderstatushistory WHERE id = %s",
                (id,)
            )
            result = cur.fetchone()
            if result:
                return cls(
                    order_status_history_id=result[0],
                    order_id=result[1],
                    status=result[2],
                    timestamp=result[3]
                )
            return None

    @classmethod
    def add_status_entry(cls, conn: object, order_id: int, new_status: str) -> object:
        """Add new status entry and update order's current status"""
        try:
            with conn.cursor() as cur:
                # Add to history
                cur.execute(
                    """INSERT INTO orderstatushistory 
                    (order_id, status) 
                    VALUES (%s, %s, %s) 
                    RETURNING history_id, changed_at""",
                    (order_id, new_status, datetime.datetime.now())
                )

                # Update order's current status
                cur.execute(
                    "UPDATE orders SET status = %s WHERE order_id = %s",
                    (new_status, order_id)
                )

                conn.commit()
                return True
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Status update failed: {e}")
            return False

    def to_dict(self) -> dict:
        """Convert to API-friendly format"""
        return {
            'order_status_history_id': self.order_status_history_id,
            'order_id': self.order_id,
            'status': self.status,
            'timestamp': self.timestamp
        }