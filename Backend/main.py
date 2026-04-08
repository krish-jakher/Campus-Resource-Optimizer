from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import database
import model
import os

app = FastAPI(title="Campus Multi-Model AI Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    database.create_tables()
    model.train_all_models()

class BookingRequest(BaseModel):
    resource_id: int
    user_name: str
    start_time: str
    end_time: str

class LoginRequest(BaseModel):
    username: str
    password: str

class BookReservationRequest(BaseModel):
    book_id: int
    user_name: str
    booking_date: str

class SeatBookingRequest(BaseModel):
    seat_id: int
    user_name: str
    start_time: str
    end_time: str

@app.get("/api/resources")
def read_resources():
    return database.get_all_resources()

@app.get("/api/resources/{resource_id}")
def read_resource(resource_id: int):
    resource = database.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@app.post("/api/book")
def book_resource(req: BookingRequest):
    resource = database.get_resource(req.resource_id)
    if not resource:
         raise HTTPException(status_code=404, detail="Resource not found")
    if not resource['is_available']:
        raise HTTPException(status_code=400, detail="Resource is currently not available")

    # Rule: If sports, check if they have read a book
    is_sports = resource['type'] == 'Sports'
    has_read_book = database.check_sports_eligibility(req.user_name)
    
    msg = "Booking request submitted successfully! Awaiting Admin Approval."
    if is_sports and not has_read_book:
        msg = "Sports booking submitted! (Note: Paid Access required as no books were issued this month)."

    success = database.book_resource(req.resource_id, req.user_name, req.start_time, req.end_time)
    if success:
        return {"message": msg}
    else:
        raise HTTPException(status_code=400, detail="Booking failed")

@app.post("/api/login")
def login_user(req: LoginRequest):
    if req.username == "admin" and req.password == "admin123":
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

# ----------------------------------------------------
# ADMIN CONTROL ENDPOINTS
# ----------------------------------------------------
@app.get("/api/admin/requests")
def read_requests():
    return database.get_pending_bookings()

@app.post("/api/admin/requests/{booking_id}/approve")
def approve_request(booking_id: int, category: str = "Resource"):
    if database.approve_booking(booking_id, category):
        return {"message": "Booking approved"}
    raise HTTPException(status_code=400, detail="Failed to approve booking")

@app.post("/api/admin/requests/{booking_id}/reject")
def reject_request(booking_id: int, category: str = "Resource"):
    if database.reject_booking(booking_id, category):
         return {"message": "Booking rejected"}
    raise HTTPException(status_code=400, detail="Failed to reject booking")

@app.put("/api/admin/resources/{resource_id}/toggle")
def toggle_resource(resource_id: int):
    if database.toggle_resource_availability(resource_id):
        return {"message": "Resource availability toggled"}
    raise HTTPException(status_code=400, detail="Failed to toggle resource")

# ----------------------------------------------------
# 3 NEW AI ENDPOINTS
# ----------------------------------------------------

@app.get("/api/predict/room")
def predict_room(temp: float, light: float, sound: float, co2: float):
    count = model.predict_room_occupancy(temp, light, sound, co2)
    return {"predicted_count": round(count, 1)}

@app.get("/api/predict/seat")
def predict_seat(hour: int, day_of_week: str, noise: float):
    prob = model.predict_seat_occupancy(hour, day_of_week, noise)
    return {"occupied_probability": round(prob * 100, 2)}

@app.get("/api/predict/satisfaction")
def predict_satisfaction(duration: float, books: int, digital: float, logins: int):
    score = model.predict_user_satisfaction(duration, books, digital, logins)
    return {"predicted_satisfaction": round(score, 1)}

# ----------------------------------------------------
# LIBRARY AND HISTORY ENDPOINTS
# ----------------------------------------------------
@app.get("/api/books")
def read_books():
    return database.get_all_books()

@app.post("/api/books/reserve")
def api_reserve_book(req: BookReservationRequest):
    # Rule: Must play some sports to issue book
    if not database.check_book_eligibility(req.user_name):
        raise HTTPException(status_code=403, detail="Activity Required: You must participate in a sports activity this month to reserve books!")
        
    if database.reserve_book(req.book_id, req.user_name, req.booking_date):
        return {"message": "Book reserved successfully for pickup!"}
    raise HTTPException(status_code=400, detail="Failed to reserve book")

@app.get("/api/user/{user_name}/history")
def read_user_history(user_name: str):
    return database.get_user_history(user_name)

@app.get("/api/user/{user_name}/eligibility")
def check_user_eligibility(user_name: str):
    return {
        "can_access_sports_free": database.check_sports_eligibility(user_name),
        "can_reserve_books": database.check_book_eligibility(user_name)
    }

@app.delete("/api/bookings/{booking_id}")
def api_cancel_resource_booking(booking_id: int):
    if database.cancel_resource_booking(booking_id):
        return {"message": "Resource booking cancelled"}
    raise HTTPException(status_code=400, detail="Failed to cancel booking")

@app.delete("/api/books/reservations/{reservation_id}")
def api_cancel_book_reservation(reservation_id: int):
    if database.cancel_book_reservation(reservation_id):
        return {"message": "Book reservation cancelled"}
    raise HTTPException(status_code=400, detail="Failed to cancel reservation")

# ----------------------------------------------------
# SEAT ENDPOINTS
# ----------------------------------------------------
@app.get("/api/seats")
def read_seats():
    return database.get_all_seats()

@app.post("/api/seats/book")
def api_book_seat(req: SeatBookingRequest):
    if database.book_library_seat(req.seat_id, req.user_name, req.start_time, req.end_time):
        return {"message": "Seat booking request submitted"}
    raise HTTPException(status_code=400, detail="Failed to submit seat booking")

@app.delete("/api/seats/bookings/{booking_id}")
def api_cancel_seat_booking(booking_id: int):
    if database.cancel_seat_booking(booking_id):
        return {"message": "Seat booking cancelled"}
    raise HTTPException(status_code=400, detail="Failed to cancel seat booking")

# ----------------------------------------------------
# LIBRARY OPTIMIZER ENDPOINT
# ----------------------------------------------------
@app.get("/api/optimization/library")
def optimize_library():
    books = database.get_all_books()
    optimizations = []
    
    for book in books:
        t_copies = book.get("total_copies", 10)
        a_copies = book.get("available_copies", 10)
        w_count = book.get("waitlist_count", 0)
        
        active_checkouts = t_copies - a_copies
        demand = w_count + active_checkouts
        ratio = demand / max(1, t_copies)
        
        status = "Normal"
        loan_period = "14 Days"
        loan_justification = "Standard checkout duration."
        acquisition = "No action needed"
        alert = "None"
        
        if ratio > 3.0:
            status = "Critical Shortage"
            loan_period = "3 Days"
            loan_justification = "Demand exceeds 300% of inventory."
            buy_copies = max(1, demand // 3) 
            acquisition = f"Buy {buy_copies} Copies"
            if book.get("upcoming_exam_date"):
                alert = f"Exam on {book['upcoming_exam_date']} - loan massively sped up!"
            else:
                alert = "Severe shortage! Loan duration severely reduced."
        elif ratio > 1.5:
            status = "High Demand"
            loan_period = "7 Days"
            loan_justification = "Demand exceeds 150% of inventory."
            buy_copies = max(1, demand // 3)
            if buy_copies > 0:
                acquisition = f"Buy {buy_copies} Copies"
            else:
                acquisition = "Monitor closely"
                
            if book.get("upcoming_exam_date"):
                alert = f"Exam on {book['upcoming_exam_date']} - loan duration halved."
            else:
                alert = "High waitlist! Loan duration halved."
        
        optimizations.append({
            "id": book["id"],
            "title": book["title"],
            "author": book["author"],
            "total_copies": t_copies,
            "available_copies": a_copies,
            "waitlist_count": w_count,
            "demand": demand,
            "demand_ratio": round(ratio * 100, 1),
            "resource_status": status,
            "adjusted_loan_period": loan_period,
            "justification": loan_justification,
            "acquisition_recommendation": acquisition,
            "alerts": alert
        })
        
    return optimizations

# Mount frontend only when running locally (not on Vercel)
if not os.environ.get('VERCEL'):
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
    if os.path.isdir(frontend_dir):
        from fastapi.staticfiles import StaticFiles
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
