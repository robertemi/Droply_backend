from typing import Optional

from models.Order import Order
from models.OrderStatusHistory import OrderStatusHistory
import datetime

class OrderService:
    @staticmethod
    def create_order(
            conn,
            company_id: int,
            pickup_address: str,
            delivery_address: str,
            courier_id: Optional[int] = None
    ):
        """Handles full order creation workflow"""
        try:
            # Create the order
            order = Order.create(
                conn=conn,
                company_id=company_id,
                pickup_address=pickup_address,
                delivery_address=delivery_address,
                status='Created',
                created_at=datetime.datetime.now(),
                courier_id=courier_id,
            )
            return order

        except Exception as e:
            conn.rollback()
            print(f"Order creation failed: {str(e)}")
            return None

    # private method used as helper for assigned courier
    @staticmethod
    def _update_to_assigned(conn, order_id: int, courier_id: int) -> bool:
        """Internal method for assignment workflow"""
        try:
            # Update order status
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE orders SET status = 'Assigned' WHERE order_id = %s",
                    (order_id,)
                )

            # Record status change
            OrderStatusHistory.add_status_entry(
                conn=conn,
                order_id=order_id,
                new_status='Assigned'
            )

            return True
        except Exception as e:
            print(f"Assignment failed: {str(e)}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_unassigned_order(conn):
        try:
            orders = Order.get_unassigned_orders(conn)
            return orders
        except Exception as e:
            return print(f"Unexpected")

    @staticmethod
    def get_company_orders(conn, company_id):
        try:
            orders = Order.get_company_orders(conn, company_id)
            return [order.to_dict() for order in orders]
        except Exception as e:
            print(f"Unexpected: {e}")
            return []

    @staticmethod
    def delete_order(conn, order_id):
        try:
            Order.delete_order(conn, order_id)
        except Exception as e:
            print(f"Unexpected: {e}")

    @staticmethod
    def assign_courier(
            conn,
            order_id: int,
            courier_id: int
    ) -> bool:
        """Assigns courier to existing order"""
        order = Order.get_by_id(conn, order_id)
        if not order:
            return False

        return OrderService._update_to_assigned(conn, order_id, courier_id)

