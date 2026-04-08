# 🎓 CROptimizer — Campus Resource Optimizer

> **A Multi-Model AI-Powered Smart Campus Dashboard** built for modern university infrastructure. Dynamically tracks, predicts, and manages campus resources with intelligent cross-module eligibility rules between Library and Sports systems.

---

## 📸 Overview

CROptimizer is an all-in-one campus management platform that brings together **Room Booking**, **Library Catalog**, **Seat Booking**, **Sports Facility Management**, and **Multi-Model AI Predictions** into a single premium glassmorphism-styled dashboard.

---

## ✨ Features

### 📚 Library System
- Browse the full physical library catalog with real-time availability
- **Book Reservation** — Reserve books for in-person pickup
- **Calculus Optimization Engine** — AI-driven inventory rule engine:
  - Demand/Supply ratio monitoring
  - Automatic loan period reduction: `14 days → 7 days → 3 days` based on demand surges
  - Acquisition recommendations for stock replenishment

### 🏀 Sports Facilities
- Full catalog of campus sports assets: **Cricket Kit, Basketball Arena, Football Turf, Skating Rink, Volleyball Court, Table Tennis Hall, Chess Lounge**
- Zone-aware availability with real-time booking

### 🔗 Cross-Module Eligibility Rules
The platform links **Library usage** and **Sports participation** together:

| Action | Requirement |
|---|---|
| Access **Sports for Free** | Must have reserved ≥ 1 book this month |
| Access **Sports (Paid)** | No book issued → $5/hr charged |
| **Reserve a Book** | Must have participated in sports this month |

> These rules encourage balanced academic and physical activity among students.

### 📖 Seat Booking
- Individual library study seats in three dedicated zones:
  - 🔵 **Quiet Zone** — Solo focused study
  - 🟠 **Collaborative Zone** — Group work
  - 🟢 **Lab Zone** — Computer/equipment access
- Each seat goes through an Admin approval workflow

### 🤖 Multi-Model AI Insights
Three independent prediction models running simultaneously:

| Model | Dataset | Predicts |
|---|---|---|
| Room Sensoring | `Occupancy_Estimation.csv` | Live occupant count via IoT (Temp, Light, CO2, Sound) |
| Seat Probability | `library_seat_occupancy_dataset.csv` | % chance a seat is occupied by Time/Day/Noise |
| Student Satisfaction | `smart_library_data.csv` | Satisfaction score (out of 5) from digital footprint |

### 🔐 Dual Authentication
| Role | Access Level |
|---|---|
| **Guest** | Browse resources only |
| **Student** | Book rooms, seats, sports, reserve books, view history |
| **Admin** | Approve/reject all requests, toggle availability, view Book Inventory optimizer |

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML5, CSS3, JavaScript (ES6+) |
| Styling | Glassmorphism dark-mode UI, Google Fonts (Inter, Outfit) |
| Backend | Python 3.8+ + FastAPI |
| Database | SQLite (zero-config, auto-generated) |
| ML Engine | Scikit-Learn (RandomForest), Pandas, NumPy |
| Server | Uvicorn ASGI |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** → [Download](https://www.python.org/downloads/)
- **Node.js & npm** (optional, for standalone frontend serving) → [Download](https://nodejs.org/)
- **Git** → [Download](https://git-scm.com/)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd "hackathon 1st"
```

### 2. Install Python Dependencies

```powershell
pip install -r backend/requirements.txt
```

### 3. (Optional) Add the Books Dataset

For a fully populated library catalog, download the Goodreads books dataset from Kaggle:

👉 [Goodreads Books Dataset — Kaggle](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks)

1. Download and rename the file to `books_dataset.csv`
2. Place it inside the `backend/` folder

> Without this file, the app still works with 3 built-in dummy books.

### 4. Start the Backend Server

```powershell
cd backend
python -m uvicorn main:app --reload
```

> **First-run note:** The AI models train from scratch on first launch and save `.pkl` state files. This takes **30–60 seconds** — subsequent starts are instant.

### 5. Open the App

Navigate to in your browser:
```
http://127.0.0.1:8000/
```

---

## 🔑 Test Credentials

| Role | Name / Username | Password |
|---|---|---|
| **Student** | Any name (e.g. `Alice`) | `student123` |
| **Admin** | `admin` | `admin123` |

---

## 📡 API Reference

### Resources & Booking
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/resources` | All rooms and facilities |
| `POST` | `/api/book` | Submit a room/facility booking |
| `DELETE` | `/api/bookings/{id}` | Cancel a booking |

### Library
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/books` | Full library catalog |
| `POST` | `/api/books/reserve` | Reserve a book for pickup |
| `DELETE` | `/api/books/reservations/{id}` | Cancel a book reservation |
| `GET` | `/api/optimization/library` | Run the Calculus Optimizer engine |

### Library Seats
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/seats` | All library study seats |
| `POST` | `/api/seats/book` | Book a study seat |
| `DELETE` | `/api/seats/bookings/{id}` | Cancel a seat booking |

### AI Predictions
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/predict/room` | Occupant count prediction |
| `GET` | `/api/predict/seat` | Seat occupancy probability |
| `GET` | `/api/predict/satisfaction` | Student satisfaction score |

### Users & Admin
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/user/{name}/history` | Full booking history for a student |
| `GET` | `/api/user/{name}/eligibility` | Library–Sports eligibility status |
| `POST` | `/api/login` | Admin login |
| `GET` | `/api/admin/requests` | All pending booking requests |
| `POST` | `/api/admin/requests/{id}/approve` | Approve a request |
| `POST` | `/api/admin/requests/{id}/reject` | Reject a request |
| `PUT` | `/api/admin/resources/{id}/toggle` | Toggle resource availability |

---

## 📁 Project Structure

```
hackathon 1st/
├── backend/
│   ├── main.py              # FastAPI application & all API routes
│   ├── database.py          # SQLite schema, CRUD operations, eligibility logic
│   ├── model.py             # Scikit-Learn ML models (train & predict)
│   ├── requirements.txt     # Python dependencies
│   └── campus_resources.db  # Auto-generated SQLite database
├── frontend/
│   ├── index.html           # Full single-page application layout
│   ├── app.js               # All frontend logic (auth, fetching, rendering)
│   └── style.css            # Glassmorphism dark-mode design system
└── README.md
```

---

## 🧪 Testing the Cross-Module Rules

1. **Login** as a student (`student123`)
2. Go to **Library Catalog** → You'll see a warning: *"Must participate in sports first"*
3. Go to **Sports Facilities** → Book any sport (e.g. Chess). Notice it says *"Paid Access"* since no book was issued
4. Login as **Admin** and **Approve** the sports booking
5. Switch back to Student → Go to **Library Catalog** → Warning gone! Reserve a book now
6. After book approval → Go to **Sports** → Access is now **FREE** ✅

---

## 🤝 Contributing

This project was built for hackathon demonstration. To extend it:

- Connect IoT sensors to the AI models for real-time data
- Deploy to [Render](https://render.com) or [Railway](https://railway.app) for live hosting
- Add email/SMS notifications for booking approvals
- Integrate a real authentication system (e.g. JWT tokens)

Feel free to fork and submit pull requests!

---

## 📄 License

MIT License — Free to use, modify, and distribute.
