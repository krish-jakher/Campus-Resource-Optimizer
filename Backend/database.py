import sqlite3
from sqlite3 import Error
import os
import pandas as pd
import random

DB_FILE = "campus_resources.db"
BOOKS_DATA = "books_dataset.csv"

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    capacity INTEGER NOT NULL,
                    is_available BOOLEAN NOT NULL DEFAULT 1,
                    location TEXT
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    FOREIGN KEY (resource_id) REFERENCES resources (id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT,
                    is_available BOOLEAN NOT NULL DEFAULT 1,
                    total_copies INTEGER DEFAULT 10,
                    available_copies INTEGER DEFAULT 10,
                    waitlist_count INTEGER DEFAULT 0,
                    historical_checkouts INTEGER DEFAULT 50,
                    upcoming_exam_date TEXT
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS book_reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    booking_date TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending pickup',
                    FOREIGN KEY (book_id) REFERENCES books (id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS library_seats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seat_name TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    is_available BOOLEAN NOT NULL DEFAULT 1
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seat_bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seat_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    FOREIGN KEY (seat_id) REFERENCES library_seats (id)
                );
            """)
            conn.commit()
            
            # Resources Dummies
            cursor.execute("SELECT count(*) FROM resources")
            if cursor.fetchone()[0] == 0:
                dummy_data = [
                    ('Main Library Room A', 'Study Room', 4, 1, 'Library Floor 1'),
                    ('Computer Lab 101', 'Lab', 30, 1, 'Engineering Building'),
                    ('3D Printer X1', 'Equipment', 1, 1, 'MakerSpace'),
                    ('Conference Room B', 'Meeting Room', 12, 1, 'Student Union'),
                    ('Basketball Court 1', 'Sports', 20, 1, 'Sports Complex'),
                    ('Cricket Kit Premium', 'Sports', 1, 1, 'Equipment Office'),
                    ('Main Basketball Arena', 'Sports', 50, 1, 'Sports Center'),
                    ('Football Turf A', 'Sports', 22, 1, 'Outdoor Fields'),
                    ('Skating Rink', 'Sports', 15, 1, 'East Wing'),
                    ('Volleyball Court', 'Sports', 12, 1, 'Sports Complex'),
                    ('Table Tennis Hall', 'Sports', 4, 1, 'Recreation Center'),
                    ('Chess Lounge', 'Sports', 2, 1, 'Student Union')
                ]
                cursor.executemany("INSERT INTO resources (name, type, capacity, is_available, location) VALUES (?, ?, ?, ?, ?)", dummy_data)
                conn.commit()
                
            # Seats Dummies
            cursor.execute("SELECT count(*) FROM library_seats")
            if cursor.fetchone()[0] == 0:
                dummy_seats = [
                    ('Seat Q1', 'Quiet Zone', 1), ('Seat Q2', 'Quiet Zone', 1), ('Seat Q3', 'Quiet Zone', 1), ('Seat Q4', 'Quiet Zone', 1),
                    ('Seat C1', 'Collab Zone', 1), ('Seat C2', 'Collab Zone', 1), ('Seat C3', 'Collab Zone', 1), ('Seat C4', 'Collab Zone', 1),
                    ('Seat L1', 'Lab Zone', 1), ('Seat L2', 'Lab Zone', 1), ('Seat L3', 'Lab Zone', 1), ('Seat L4', 'Lab Zone', 1)
                ]
                cursor.executemany("INSERT INTO library_seats (seat_name, zone, is_available) VALUES (?, ?, ?)", dummy_seats)
                conn.commit()
            # Books Parsing
            cursor.execute("SELECT count(*) FROM books")
            if cursor.fetchone()[0] == 0:
                if os.path.exists(BOOKS_DATA):
                    print(f"Importing library books from {BOOKS_DATA}...")
                    df = pd.read_csv(BOOKS_DATA, on_bad_lines='skip')
                    # We look for common titles
                    title_col = 'title' if 'title' in df.columns else df.columns[1]
                    author_col = 'authors' if 'authors' in df.columns else df.columns[2]
                    isbn_col = 'isbn' if 'isbn' in df.columns else df.columns[3] if len(df.columns)>3 else None
                    
                    # Take first 150 for performance
                    data_to_insert = []
                    for idx, row in df.head(150).iterrows():
                        t = str(row[title_col])[:100]
                        a = str(row[author_col])[:100]
                        i = str(row[isbn_col]) if isbn_col else "N/A"
                        
                        # Generate random distribution for optimization testing
                        t_copies = random.randint(3, 10)
                        a_copies = random.randint(0, t_copies)
                        # Make some books have surging waitlists
                        w_count = random.choice([0, 0, 0, random.randint(1, 5), random.randint(15, 40)])
                        h_checks = random.randint(10, 100)
                        exam_date = random.choice(["2026-05-01", "2026-12-15", None, None])
                        is_avail = 1 if a_copies > 0 else 0
                        
                        data_to_insert.append((t, a, i, is_avail, t_copies, a_copies, w_count, h_checks, exam_date))
                        
                    cursor.executemany("INSERT INTO books (title, author, isbn, is_available, total_copies, available_copies, waitlist_count, historical_checkouts, upcoming_exam_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", data_to_insert)
                    conn.commit()
                    print("Imported books successfully.")
                else:
                    # Insert dummy
                    dummy_books = [
                        ('The Algorithm Design Manual', 'Steven S. Skiena', '9781849967204', 1, 5, 5, 0, 45, '2026-05-10'),
                        ('Calculus Early Transcendentals', 'James Stewart', '9781285741550', 0, 4, 0, 15, 120, '2026-04-20'),
                        ('Introduction to the Theory of Computation', 'Thomas H. Cormen', '9781133187773', 1, 8, 2, 0, 30, None)
                    ]
                    cursor.executemany("INSERT INTO books (title, author, isbn, is_available, total_copies, available_copies, waitlist_count, historical_checkouts, upcoming_exam_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", dummy_books)
                    conn.commit()

        except Error as e:
            print(e)
        finally:
            conn.close()

# --- RESOURCES ---
def get_all_resources():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resources")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_resource(resource_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resources WHERE id=?", (resource_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def book_resource(resource_id, user_name, start_time, end_time):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bookings (resource_id, user_name, start_time, end_time, status) VALUES (?, ?, ?, ?, 'pending')",
                       (resource_id, user_name, start_time, end_time))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def toggle_resource_availability(resource_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT is_available FROM resources WHERE id = ?", (resource_id,))
        res = cursor.fetchone()
        if res:
            new_status = 0 if res['is_available'] else 1
            cursor.execute("UPDATE resources SET is_available = ? WHERE id = ?", (new_status, resource_id))
            conn.commit()
            return True
        return False
    except: return False
    finally: conn.close()

# --- ADMIN APPROVALS ---
def get_pending_bookings():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, b.resource_id as item_id, b.user_name, b.start_time, b.end_time, b.status, r.name as item_name, 'Resource' as category 
        FROM bookings b JOIN resources r ON b.resource_id = r.id WHERE b.status = 'pending'
    ''')
    res_rows = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT sb.id, sb.seat_id as item_id, sb.user_name, sb.start_time, sb.end_time, sb.status, s.seat_name as item_name, 'Seat' as category 
        FROM seat_bookings sb JOIN library_seats s ON sb.seat_id = s.id WHERE sb.status = 'pending'
    ''')
    seat_rows = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return res_rows + seat_rows

def approve_booking(booking_id, category='Resource'):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        if category == 'Resource':
            cursor.execute("UPDATE bookings SET status = 'approved' WHERE id = ?", (booking_id,))
            cursor.execute("SELECT resource_id FROM bookings WHERE id = ?", (booking_id,))
            res = cursor.fetchone()
            if res: cursor.execute("UPDATE resources SET is_available = 0 WHERE id = ?", (res['resource_id'],))
        elif category == 'Seat':
            cursor.execute("UPDATE seat_bookings SET status = 'approved' WHERE id = ?", (booking_id,))
            cursor.execute("SELECT seat_id FROM seat_bookings WHERE id = ?", (booking_id,))
            res = cursor.fetchone()
            if res: cursor.execute("UPDATE library_seats SET is_available = 0 WHERE id = ?", (res['seat_id'],))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def reject_booking(booking_id, category='Resource'):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        if category == 'Resource':
            cursor.execute("UPDATE bookings SET status = 'rejected' WHERE id = ?", (booking_id,))
        elif category == 'Seat':
            cursor.execute("UPDATE seat_bookings SET status = 'rejected' WHERE id = ?", (booking_id,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- BOOKS ---
def get_all_books():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def reserve_book(book_id, user_name, date):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO book_reservations (book_id, user_name, booking_date) VALUES (?, ?, ?)",
                       (book_id, user_name, date))
        cursor.execute("UPDATE books SET is_available = 0 WHERE id = ?", (book_id,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- USER HISTORY ---
def get_user_history(user_name):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.id as booking_id, b.start_time, b.end_time, b.status, r.name as item_name, 'Resource' as category 
        FROM bookings b JOIN resources r ON b.resource_id = r.id WHERE b.user_name = ?
    ''', (user_name,))
    room_bookings = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT res.id as booking_id, res.booking_date as start_time, '-' as end_time, res.status, bk.title as item_name, 'Book' as category 
        FROM book_reservations res JOIN books bk ON res.book_id = bk.id WHERE res.user_name = ?
    ''', (user_name,))
    book_reservations = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT sb.id as booking_id, sb.start_time, sb.end_time, sb.status, s.seat_name as item_name, 'Seat' as category 
        FROM seat_bookings sb JOIN library_seats s ON sb.seat_id = s.id WHERE sb.user_name = ?
    ''', (user_name,))
    seat_bookings = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return room_bookings + book_reservations + seat_bookings

def cancel_resource_booking(booking_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
        # Optional: could un-unavailable the resource if it was already 'approved'.
        cursor.execute("SELECT resource_id, status FROM bookings WHERE id = ?", (booking_id,))
        res = cursor.fetchone()
        if res and res['status'] == 'approved':
           cursor.execute("UPDATE resources SET is_available = 1 WHERE id = ?", (res['resource_id'],))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def cancel_book_reservation(reservation_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE book_reservations SET status = 'cancelled' WHERE id = ?", (reservation_id,))
        cursor.execute("SELECT book_id FROM book_reservations WHERE id = ?", (reservation_id,))
        res = cursor.fetchone()
        if res: cursor.execute("UPDATE books SET is_available = 1 WHERE id = ?", (res['book_id'],))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- SEATS ---
def get_all_seats():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM library_seats")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def book_library_seat(seat_id, user_name, start_time, end_time):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO seat_bookings (seat_id, user_name, start_time, end_time, status) VALUES (?, ?, ?, ?, 'pending')",
                       (seat_id, user_name, start_time, end_time))
        conn.commit()
        return True
    except: return False
    finally: conn.close()
    
def cancel_seat_booking(booking_id):
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE seat_bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
        cursor.execute("SELECT seat_id, status FROM seat_bookings WHERE id = ?", (booking_id,))
        res = cursor.fetchone()
        if res and res['status'] == 'approved':
           cursor.execute("UPDATE library_seats SET is_available = 1 WHERE id = ?", (res['seat_id'],))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- ELIGIBILITY RULES ---
def check_sports_eligibility(user_name):
    """Requires 1 book in the last 30 days (status: pending pickup or approved)"""
    conn = create_connection()
    cursor = conn.cursor()
    # Simplified month check: any reservation exists
    cursor.execute("SELECT count(*) FROM book_reservations WHERE user_name = ? AND status != 'cancelled' AND status != 'rejected'", (user_name,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def check_book_eligibility(user_name):
    """Requires playing some sports (status: approved or pending)"""
    conn = create_connection()
    cursor = conn.cursor()
    # Check if user has booked a resource of type 'Sports'
    cursor.execute("""
        SELECT count(*) 
        FROM bookings b 
        JOIN resources r ON b.resource_id = r.id 
        WHERE b.user_name = ? AND r.type = 'Sports' AND b.status != 'cancelled' AND b.status != 'rejected'
    """, (user_name,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

if __name__ == '__main__':
    create_tables()
