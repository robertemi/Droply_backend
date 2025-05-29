from datetime import datetime
from typing import Optional
import random
from models.OrderStatusHistory import OrderStatusHistory
import psycopg2

class Order():
    def __init__(self, order_id: int, company_id: int, pickup_address: str, delivery_address: str, status: str, created_at: datetime, awb: str):
        self.order_id = order_id
        self.company_id = company_id
        self.pickup_address = pickup_address
        self.delivery_address = delivery_address
        self.status = status
        self.created_at = created_at
        self.awb = awb

    @classmethod
    def generate_awb(self):
        # DRP-12345678-RO
        random_8_digit = random.randint(10_000_000, 99_999_999)
        return str('DRP-' + str(random_8_digit) + '-RO')

    @classmethod
    def create(cls, conn, company_id, pickup_address, delivery_address, status, created_at):
        awb = cls.generate_awb()
        try:
            with conn.cursor() as cur:
                # handle case of no assigned courier
                    cur.execute(
                        "INSERT INTO orders (company_id, pickup_address, delivery_address, status, created_at, awb) "
                        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING order_id",
                        (company_id, pickup_address, delivery_address, status, created_at, awb)
                    )
                    order_id = cur.fetchone()[0]
                    conn.commit()
                    return cls(order_id, company_id, pickup_address, delivery_address, status, created_at, awb)

        except psycopg2.Error as e:
            conn.rollback()
            print(f"Order creation failed: {e}")
            return None

    # returns orders that a courier has accepted
    @classmethod
    def get_assigned_orders(cls, conn, courier_id):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT orders.order_id, orders.company_id, orders.pickup_address, orders.delivery_address, "
                    "orders.status, orders.created_at, orders.awb "
                    "FROM orders "
                    "INNER JOIN orderstatushistory ON orders.order_id = orderstatushistory.order_id "
                    "WHERE orderstatushistory.courier_id = %s",
                    (courier_id,)
                )
                results = cur.fetchall()
                return [
                    cls(*row) for row in results
                ]
        except psycopg2.Error as e:
            print(f"Fetch assigned orders failed: {e}")
            return []

    @classmethod
    def get_unassigned_orders(cls, conn):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT order_id, company_id, pickup_address, delivery_address, status, created_at, awb "
                    "FROM orders WHERE status = 'Created' "
                )
                results = cur.fetchall()
                return [
                    cls(*row) for row in results
                ]
        except psycopg2.Error as e:
            print(f"Fetch unassigned orders failed: {e}")
            return []

    @classmethod
    def get_company_orders(cls, conn, company_id):
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM orders WHERE company_id = %s",
                (company_id,)
            )

            results = cur.fetchall()
            return [
                cls(*row) for row in results
            ]

    @classmethod
    def assign_order(cls, conn, courier_id: int, order_id: int) -> bool:
        """Assign order to courier and mark as unavailable"""
        try:
            with conn.cursor() as cur:
                # Assign order
                cur.execute(
                    "INSERT INTO orderstatushistory (order_id, courier_id) VALUES (%s, %s)",
                    (order_id, courier_id)
                )

                cur.execute()

                # Record status change
                OrderStatusHistory.add_status_entry(
                    conn, order_id, courier_id=courier_id, new_status='Assigned'
                )

                conn.commit()
                return True
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Order assignment failed: {e}")
            return False

    @classmethod
    def get_by_id(cls, conn, id: int):
        """Retrieve order by id"""
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM orders WHERE order_id = %s",
                (id,)
            )
            result = cur.fetchone()
            if result:
                return cls(
                    order_id=result[0],
                    company_id=result[1],
                    pickup_address=result[2],
                    delivery_address=result[3],
                    status=result[4],
                    created_at=result[5],
                    awb=result[6]
                )
            return None
    @classmethod
    def delete_order(self, conn, order_id):
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM orders WHERE order_id = %s",
                (order_id,)
            )
            conn.commit()


    def to_dict(self) -> dict:
        return {
            'order_id': self.order_id,
            "company_id": self.company_id,
            'pickup_address': self.pickup_address,
            'delivery_address': self.delivery_address,
            'created_at': self.created_at,
            'status': self.status,
            'awb': self.awb
        }
         
    
    @classmethod
    def get_by_awb(cls, conn, awb: str):
        """Retrieve order by AWB number"""
        with conn.cursor() as cur:
            cur.execute(
                "SELECT order_id, company_id, pickup_address, delivery_address, status, created_at, awb FROM orders WHERE awb = %s",
                (awb,)
            )
            result = cur.fetchone()
            if result:
                return cls(
                    order_id=result[0],
                    company_id=result[1],
                    pickup_address=result[2],
                    delivery_address=result[3],
                    status=result[4],
                    created_at=result[5],
                    awb=result[6]
                )
            return None
    
    # def to_dict(self) -> dict:
    #     return {
    #         'order_id': self.order_id,
    #         "company_id": self.company_id,
    #         'pickup_address': self.pickup_address,
    #         'delivery_address': self.delivery_address,
    #         'status': self.status,
    #         'awb': self.awb,
    #         'created_at': self.created_at.isoformat() if self.created_at else None
    #     }

