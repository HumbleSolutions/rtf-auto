# model/db_manager.py
import sqlite3
import os
from datetime import datetime

DEFAULT_DB = "rtf_auto.db"

class DBManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or DEFAULT_DB
        self._run_migrations()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _run_migrations(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # model/db_manager.py (inside DBManager._run_migrations)

# —— ensure work_orders has odometer_km ——  
        cursor.execute("PRAGMA table_info(work_orders)")
        cols = [col[1] for col in cursor.fetchall()]
        if "odometer_km" not in cols:
            cursor.execute("""
                ALTER TABLE work_orders
                ADD COLUMN odometer_km INTEGER DEFAULT 0
            """)


        cursor.execute("PRAGMA table_info(vehicles)")
        columns = [col[1] for col in cursor.fetchall()]
        if "odometer_km" not in columns:
            cursor.execute("ALTER TABLE vehicles ADD COLUMN odometer_km INTEGER DEFAULT 0")

        # USERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        """)

        # CUSTOMERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                email TEXT
            )
        """)

        # VEHICLES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                make TEXT,
                model TEXT,
                year TEXT,
                vin TEXT,
                odometer_km INTEGER DEFAULT 0,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            )
        """)

        # WORK ORDERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                issue TEXT,
                notes TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rate REAL DEFAULT 65.0,
                hourly_rate REAL DEFAULT 100.0,
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
            )
        """)

        # SERVICES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_order_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_order_id INTEGER,
                service_type TEXT,
                FOREIGN KEY(work_order_id) REFERENCES work_orders(id)
            )
        """)

        # MECHANIC HOURS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanic_hours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_order_id INTEGER,
                mechanic TEXT,
                hours REAL,
                date TEXT,
                FOREIGN KEY(work_order_id) REFERENCES work_orders(id)
            )
        """)
        # VIN Cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vin_cache (
                vin TEXT PRIMARY KEY,
                make TEXT,
                model TEXT,
                year TEXT,
                cached_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


        # PARTS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_order_parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_order_id INTEGER,
                part_name TEXT,
                quantity INTEGER,
                unit_price REAL,
                cost REAL DEFAULT 0.0,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(work_order_id) REFERENCES work_orders(id)
            )
        """)

        conn.commit()
        conn.close()

    def get_notes_for_work_order(self, work_order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT notes FROM work_orders WHERE id = ?", (work_order_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else ""

    def update_work_order_notes(self, work_order_id, notes):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE work_orders SET notes = ? WHERE id = ?", (notes, work_order_id))
        conn.commit()
        conn.close()

    def get_work_orders_by_status(self, status="In Progress"):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT work_orders.id,
                v.id || ' - ' || c.first_name || ' ' || c.last_name || ' ' || v.make || ' ' || v.model || ' ' || v.year,
                work_orders.issue, work_orders.notes, work_orders.status, work_orders.rate
            FROM work_orders
            JOIN vehicles v ON work_orders.vehicle_id = v.id
            JOIN customers c ON v.customer_id = c.id
            WHERE work_orders.status = ?
            ORDER BY work_orders.id DESC
        """, (status,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_all_work_orders(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT work_orders.id,
                v.id || ' - ' || c.first_name || ' ' || c.last_name || ' ' || v.make || ' ' || v.model || ' ' || v.year,
                work_orders.issue,
                work_orders.notes,
                work_orders.status,
                work_orders.rate
            FROM work_orders
            JOIN vehicles v ON work_orders.vehicle_id = v.id
            JOIN customers c ON v.customer_id = c.id
            ORDER BY work_orders.id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_part_to_work_order(self, work_order_id, part_name, quantity, unit_price, cost=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO work_order_parts (work_order_id, part_name, quantity, unit_price, cost)
            VALUES (?, ?, ?, ?, ?)
        """, (work_order_id, part_name, quantity, unit_price, cost or 0.0))
        conn.commit()
        conn.close()

    def get_parts_for_work_order(self, work_order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, part_name, quantity, unit_price, cost, added_at
            FROM work_order_parts
            WHERE work_order_id = ?
        """, (work_order_id,))
        result = cursor.fetchall()
        conn.close()
        return result

    def delete_work_order_part(self, part_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM work_order_parts WHERE id = ?", (part_id,))
        conn.commit()
        conn.close()

    def get_mechanic_hours(self, work_order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, mechanic, hours, date
            FROM mechanic_hours
            WHERE work_order_id = ?
        """, (work_order_id,))
        results = cursor.fetchall()
        conn.close()
        return results

    def add_mechanic_hours(self, work_order_id, mechanic, hours, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mechanic_hours (work_order_id, mechanic, hours, date)
            VALUES (?, ?, ?, ?)
        """, (work_order_id, mechanic, hours, date))
        conn.commit()
        conn.close()

    def delete_mechanic_hours_entry(self, entry_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mechanic_hours WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()

    def delete_work_order(self, work_order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM work_orders WHERE id = ?", (work_order_id,))
        conn.commit()
        conn.close()

    def update_work_order_status(self, work_order_id, new_status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE work_orders SET status = ? WHERE id = ?", (new_status, work_order_id))
        conn.commit()
        conn.close()

    def add_work_order(self, vehicle_id, issue, notes, status, hourly_rate):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO work_orders (vehicle_id, issue, notes, status, rate)
            VALUES (?, ?, ?, ?, ?)
        """, (vehicle_id, issue, notes, status, hourly_rate))
        conn.commit()
        conn.close()

    def update_work_order(self, work_order_id, vehicle_id, notes, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE work_orders
            SET vehicle_id = ?, notes = ?, status = ?
            WHERE id = ?
        """, (vehicle_id, notes, status, work_order_id))
        conn.commit()
        conn.close()

    def add_customer(self, first_name, last_name, phone, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (first_name, last_name, phone, email)
            VALUES (?, ?, ?, ?)
        """, (first_name, last_name, phone, email))
        conn.commit()
        conn.close()

    def update_customer(self, customer_id, first_name, last_name, phone, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers
            SET first_name = ?, last_name = ?, phone = ?, email = ?
            WHERE id = ?
        """, (first_name, last_name, phone, email, customer_id))
        conn.commit()
        conn.close()

    def get_all_customers(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, first_name, last_name, phone, email
            FROM customers
            ORDER BY last_name ASC
        """)
        results = cursor.fetchall()
        conn.close()
        return results

    def get_customer_list(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, first_name || ' ' || last_name AS full_name, phone, email
            FROM customers
            ORDER BY full_name ASC
        """)
        results = cursor.fetchall()
        conn.close()
        return results

    def get_all_vehicles(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id,
                c.first_name || ' ' || c.last_name AS owner_name,
                v.make, v.model, v.year, v.vin, v.odometer_km
            FROM vehicles v
            JOIN customers c ON v.customer_id = c.id
            ORDER BY v.year DESC
        """)
        results = cursor.fetchall()
        conn.close()
        return results


    def add_vehicle(self, customer_id, make, model, year, vin, odometer_km):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vehicles (customer_id, make, model, year, vin, odometer_km)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (customer_id, make, model, year, vin, odometer_km))
        conn.commit()
        conn.close()

    def add_work_order_service(self, work_order_id, service_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO work_order_services (work_order_id, service_type)
            VALUES (?, ?)
        """, (work_order_id, service_type))
        conn.commit()
        conn.close()

    def get_services_for_work_order(self, work_order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT service_type FROM work_order_services WHERE work_order_id = ?", (work_order_id,))
        results = cursor.fetchall()
        conn.close()
        return [r[0] for r in results]

    def delete_services_for_work_order(self, work_order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM work_order_services WHERE work_order_id = ?", (work_order_id,))
        conn.commit()
        conn.close()

    def validate_user(self, uid, pwd):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (uid, pwd))
        result = cursor.fetchone()
        conn.close()
        if result:
            return True, result[0]  # (is_valid, role)
        return False, None
    
    def update_vehicle(self, vehicle_id, customer_id, make, model, year, vin, odometer_km):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE vehicles
            SET customer_id = ?, make = ?, model = ?, year = ?, vin = ?, odometer_km = ?
            WHERE id = ?
        """, (customer_id, make, model, year, vin, odometer_km, vehicle_id))
        conn.commit()
        conn.close()

    def get_cached_vin(self, vin):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT make, model, year FROM vin_cache WHERE vin = ?", (vin,))
        row = cursor.fetchone()
        conn.close()
        return row if row else None
    
    
    def cache_vin(self, vin, make, model, year):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO vin_cache (vin, make, model, year)
            VALUES (?, ?, ?, ?)
        """, (vin, make, model, year))
        conn.commit()
        conn.close()

    def get_history_by_vehicle(self, vehicle_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
              w.id,
              w.created_at,
              COALESCE(NULLIF(w.odometer_km, 0), v.odometer_km) AS km,
              w.issue,
              w.notes,
              w.status
            FROM work_orders w
            JOIN vehicles v ON w.vehicle_id = v.id
            WHERE w.vehicle_id = ?
            ORDER BY datetime(w.created_at) DESC
        """, (vehicle_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def get_history_by_customer(self, customer_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
              w.id,
              w.created_at,
              v.make, v.model, v.year,
              COALESCE(NULLIF(w.odometer_km, 0), v.odometer_km) AS km,
              w.issue,
              w.notes,
              w.status
            FROM work_orders w
            JOIN vehicles v ON w.vehicle_id = v.id
            WHERE v.customer_id = ?
            ORDER BY datetime(w.created_at) DESC
        """, (customer_id,))
        rows = cur.fetchall()
        conn.close()
        return rows