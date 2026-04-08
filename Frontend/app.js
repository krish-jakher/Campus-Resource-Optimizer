const API_BASE = "http://127.0.0.1:8000/api";
let isLoggedIn = false; // Admin status
let currentUser = localStorage.getItem('currentUser') || null; // Student status

// ---- View Toggling ----
const navs = {
    'nav-dashboard': document.getElementById('dashboard-view'),
    'nav-seats': document.getElementById('seats-view'),
    'nav-sports': document.getElementById('sports-view'),
    'nav-books': document.getElementById('books-view'),
    'nav-history': document.getElementById('history-view'),
    'nav-insights': document.getElementById('insights-view'),
    'nav-requests': document.getElementById('requests-view'),
    'nav-optimizer': document.getElementById('optimizer-view')
};

Object.keys(navs).forEach(navId => {
    const navBtn = document.getElementById(navId);
    if(!navBtn) return;
    navBtn.addEventListener('click', (e) => {
        e.preventDefault();
        // Remove active class from all
        Object.keys(navs).forEach(id => {
            const btn = document.getElementById(id);
            if(btn) btn.parentElement.classList.remove('active');
            if(navs[id]) navs[id].classList.remove('active');
        });
        
        // Add active classes
        navBtn.parentElement.classList.add('active');
        if(navs[navId]) navs[navId].classList.add('active');

        // Fire specific refresh logic
        if(navId === 'nav-insights') triggerAllPredictions();
        if(navId === 'nav-requests') loadRequests();
        if(navId === 'nav-books') loadBooks();
        if(navId === 'nav-dashboard') loadResources();
        if(navId === 'nav-optimizer') loadOptimization();
        if(navId === 'nav-seats') loadSeats();
        if(navId === 'nav-sports') loadSports();
    });
});

// ---- Resource Dashboard Logic ----
const resourcesContainer = document.getElementById('resources-container');
const statTotal = document.getElementById('stat-total');
const statAvailable = document.getElementById('stat-available');

const modal = document.getElementById('booking-modal');
const closeModal = document.getElementById('close-modal');
const bookingForm = document.getElementById('booking-form');
const bookResourceId = document.getElementById('book-resource-id');
const modalResourceName = document.getElementById('modal-resource-name');

document.addEventListener('DOMContentLoaded', () => {
    loadResources();
    setupInsightListeners();
});

async function loadResources() {
    try {
        const response = await fetch(`${API_BASE}/resources`);
        const resources = await response.json();
        
        statTotal.textContent = resources.length;
        const availableCount = resources.filter(r => r.is_available).length;
        statAvailable.textContent = availableCount;

        resourcesContainer.innerHTML = '';
        resources.forEach(resource => {
            const card = document.createElement('div');
            card.className = 'resource-card';
            
            const statusClass = resource.is_available ? 'status-available' : 'status-booked';
            const statusText = resource.is_available ? 'Available' : 'Unavailable';
            
            card.innerHTML = `
                <div class="resource-header">
                    <div>
                        <h3 class="resource-title">${resource.name}</h3>
                        <span class="resource-type">${resource.type}</span>
                    </div>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="resource-details">
                    <span>📍 ${resource.location}</span>
                    <span>👥 Capacity: ${resource.capacity}</span>
                </div>
                <div class="resource-actions">
                    <button class="btn-primary btn-full ${!resource.is_available ? 'btn-disabled' : ''}" 
                            onclick="openBookingModal(${resource.id}, '${resource.name}')"
                            ${!resource.is_available ? 'disabled' : ''}>
                        ${resource.is_available ? 'Book Now' : 'Currently Unavailable'}
                    </button>
                    ${isLoggedIn ? `<button class="btn-primary btn-full" style="margin-top: 8px; background: var(--accent-orange);" onclick="toggleResource(${resource.id})">Toggle Availability</button>` : ''}
                </div>
            `;
            resourcesContainer.appendChild(card);
        });
    } catch (error) {
        resourcesContainer.innerHTML = '<div class="loading-state">Failed to load resources.</div>';
    }
}

function openBookingModal(id, name) {
    if (!currentUser) {
        alert("Please login as a student to book resources!");
        openStudentLoginModal();
        return;
    }
    bookResourceId.value = id;
    modalResourceName.textContent = name;
    modal.classList.add('active');
}

closeModal.addEventListener('click', () => modal.classList.remove('active'));
modal.addEventListener('click', (e) => { if(e.target === modal) modal.classList.remove('active'); });

bookingForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        resource_id: parseInt(bookResourceId.value),
        user_name: currentUser,
        start_time: document.getElementById('book-start').value,
        end_time: document.getElementById('book-end').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/book`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if(response.ok) {
            const data = await response.json();
            alert(data.message);
            modal.classList.remove('active');
            bookingForm.reset();
            loadResources();
        } else {
            const err = await response.json();
            alert("Error: " + err.detail);
        }
    } catch(e) {
        alert("Failed to submit booking.");
    }
});

// ---- Library Seats Logic ----
const seatsContainer = document.getElementById('seats-container');
const seatModal = document.getElementById('seat-booking-modal');
const closeSeatModal = document.getElementById('close-seat-modal');
const seatBookingForm = document.getElementById('seat-booking-form');
const bookSeatId = document.getElementById('book-seat-id');
const modalSeatName = document.getElementById('modal-seat-name');

async function loadSeats() {
    seatsContainer.innerHTML = '<div class="loading-state">Loading library seats...</div>';
    try {
        const response = await fetch(`${API_BASE}/seats`);
        const seats = await response.json();
        
        seatsContainer.innerHTML = '';
        if(seats.length === 0) {
            seatsContainer.innerHTML = '<div class="loading-state">No seats available!</div>';
            return;
        }

        seats.forEach(seat => {
            const card = document.createElement('div');
            card.className = 'resource-card';
            
            const statusClass = seat.is_available ? 'status-available' : 'status-booked';
            const statusText = seat.is_available ? 'Available' : 'Reserved';
            
            let zoneColor = 'var(--primary)';
            if(seat.zone === 'Quiet Zone') zoneColor = 'var(--text-secondary)';
            else if(seat.zone === 'Collab Zone') zoneColor = 'var(--accent-orange)';
            else if(seat.zone === 'Lab Zone') zoneColor = 'var(--accent-green)';
            
            card.innerHTML = `
                <div class="resource-header">
                    <div>
                        <h3 class="resource-title">${seat.seat_name}</h3>
                        <span class="resource-type" style="color:${zoneColor}">🏢 ${seat.zone}</span>
                    </div>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="resource-actions" style="margin-top: auto; padding-top: 15px;">
                    <button class="btn-primary btn-full ${!seat.is_available ? 'btn-disabled' : ''}" 
                            onclick="openSeatModal(${seat.id}, '${seat.seat_name} (${seat.zone})')"
                            ${!seat.is_available ? 'disabled' : ''}>
                        ${seat.is_available ? 'Book Seat' : 'Unavailable'}
                    </button>
                </div>
            `;
            seatsContainer.appendChild(card);
        });
    } catch (error) {
        seatsContainer.innerHTML = '<div class="loading-state">Failed to load local seats.</div>';
    }
}

function openSeatModal(id, name) {
    if (!currentUser) {
        alert("Please login as a student to book study seats!");
        openStudentLoginModal();
        return;
    }
    bookSeatId.value = id;
    modalSeatName.textContent = name;
    seatModal.classList.add('active');
}

closeSeatModal.addEventListener('click', () => seatModal.classList.remove('active'));
seatModal.addEventListener('click', (e) => { if(e.target === seatModal) seatModal.classList.remove('active'); });

seatBookingForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        seat_id: parseInt(bookSeatId.value),
        user_name: currentUser,
        start_time: document.getElementById('seat-start').value,
        end_time: document.getElementById('seat-end').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/seats/book`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if(response.ok) {
            alert("Seat booking submitted! Awaiting approval.");
            seatModal.classList.remove('active');
            seatBookingForm.reset();
            loadSeats();
        } else {
            const err = await response.json();
            alert("Error: " + err.detail);
        }
    } catch(e) {
        alert("Failed to submit seat booking.");
    }
});

// ---- Sports Facilities Logic ----
const sportsContainer = document.getElementById('sports-container');
const sportsEligibilityBanner = document.getElementById('sports-eligibility-banner');

async function loadSports() {
    sportsContainer.innerHTML = '<div class="loading-state">Loading sports equipment...</div>';
    
    // Check eligibility first
    let canAccessFree = false;
    if (currentUser) {
        try {
            const res = await fetch(`${API_BASE}/user/${currentUser}/eligibility`);
            const data = await res.json();
            canAccessFree = data.can_access_sports_free;
            
            sportsEligibilityBanner.textContent = canAccessFree ? "✅ Library Requirement Met: Sports are FREE" : "⚠️ Library Requirement Not Met: Paid Access Required ($5/hr)";
            sportsEligibilityBanner.style.background = canAccessFree ? "var(--accent-green)" : "var(--accent-orange)";
            sportsEligibilityBanner.style.color = "#fff";
        } catch(e) { console.error("Eligibility check failed"); }
    } else {
        sportsEligibilityBanner.textContent = "Login as Student to check eligibility";
    }

    try {
        const response = await fetch(`${API_BASE}/resources`);
        const resources = await response.json();
        const sports = resources.filter(r => r.type === 'Sports');

        sportsContainer.innerHTML = '';
        sports.forEach(s => {
            const card = document.createElement('div');
            card.className = 'resource-card';
            
            const statusClass = s.is_available ? 'status-available' : 'status-booked';
            const statusText = s.is_available ? 'Available' : 'Reserved';
            const priceText = canAccessFree ? 'FREE' : '$5.00 / Hour';
            
            card.innerHTML = `
                <div class="resource-header">
                    <div>
                        <h3 class="resource-title">${s.name}</h3>
                        <span class="resource-type">🏀 ${s.type}</span>
                    </div>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="resource-details">
                    <span>📍 ${s.location}</span>
                    <span>💰 Access: <strong>${priceText}</strong></span>
                </div>
                <div class="resource-actions" style="margin-top:auto">
                    <button class="btn-primary btn-full ${!s.is_available ? 'btn-disabled' : ''}" 
                            onclick="openBookingModal(${s.id}, '${s.name}')"
                            ${!s.is_available ? 'disabled' : ''}>
                        ${s.is_available ? (canAccessFree ? 'Book for Free' : 'Book (Paid Access)') : 'Unavailable'}
                    </button>
                </div>
            `;
            sportsContainer.appendChild(card);
        });
    } catch (error) {
        sportsContainer.innerHTML = '<div class="loading-state">Failed to load sports equipment.</div>';
    }
}

// ---- Library Catalog Logic ----
const booksContainer = document.getElementById('books-container');
const bookModal = document.getElementById('book-reserve-modal');
const closeBookModal = document.getElementById('close-book-modal');
const bookReserveForm = document.getElementById('book-reserve-form');

async function loadBooks() {
    booksContainer.innerHTML = '<div class="loading-state">Loading library catalog...</div>';
    
    // Check eligibility for books
    let canReserveBooks = false;
    if (currentUser) {
        try {
            const res = await fetch(`${API_BASE}/user/${currentUser}/eligibility`);
            const data = await res.json();
            canReserveBooks = data.can_reserve_books;
            
            if (!canReserveBooks) {
                const warn = document.createElement('div');
                warn.style = "background: rgba(255, 71, 87, 0.1); border-left: 4px solid var(--accent-red); padding: 15px; margin-bottom: 20px; border-radius: 8px; color: #fff; font-size: 0.9rem;";
                warn.innerHTML = "<strong>🛑 Sports Requirement Needed:</strong> You have to participate in some sports activity this month to issue/reserve books!";
                booksContainer.parentElement.insertBefore(warn, booksContainer);
                // Remove old warnings if multiple refreshes
                const oldWarns = booksContainer.parentElement.querySelectorAll('div[style*="border-left: 4px solid var(--accent-red)"]');
                if(oldWarns.length > 1) oldWarns[0].remove();
            } else {
                // Remove warnings if exists
                const oldWarns = booksContainer.parentElement.querySelectorAll('div[style*="border-left: 4px solid var(--accent-red)"]');
                oldWarns.forEach(w => w.remove());
            }
        } catch(e) {}
    }

    try {
        const response = await fetch(`${API_BASE}/books`);
        const books = await response.json();
        
        booksContainer.innerHTML = '';
        if(books.length === 0) {
            booksContainer.innerHTML = '<div class="loading-state">No books available! (Did you download the kaggle dataset?)</div>';
            return;
        }

        books.forEach(b => {
            const card = document.createElement('div');
            card.className = 'resource-card';
            
            const statusClass = b.is_available ? 'status-available' : 'status-booked';
            const statusText = b.is_available ? 'Available' : 'Reserved';
            
            card.innerHTML = `
                <div class="resource-header">
                    <div>
                        <h3 class="resource-title" style="white-space: normal; line-height: 1.2;">${b.title}</h3>
                        <span class="resource-type">📖 Book</span>
                    </div>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="resource-details" style="margin-top: 10px;">
                    <span>✍️ Author: ${b.author}</span>
                    <span>🏷️ ISBN: ${b.isbn}</span>
                </div>
                <div class="resource-actions" style="margin-top: auto;">
                    <button class="btn-primary btn-full ${!b.is_available ? 'btn-disabled' : ''}" 
                            onclick="openBookModal(${b.id}, '${b.title.replace(/'/g, "\\'")}')"
                            ${!b.is_available ? 'disabled' : ''}>
                        ${b.is_available ? 'Reserve for Pickup' : 'Unavailable'}
                    </button>
                </div>
            `;
            booksContainer.appendChild(card);
        });
    } catch (error) {
        booksContainer.innerHTML = '<div class="loading-state">Failed to load catalog.</div>';
    }
}

function openBookModal(id, title) {
    if (!currentUser) {
        alert("Please login as a student to reserve books!");
        openStudentLoginModal();
        return;
    }
    document.getElementById('reserve-book-id').value = id;
    document.getElementById('modal-book-title').textContent = title;
    bookModal.classList.add('active');
}

closeBookModal.addEventListener('click', () => bookModal.classList.remove('active'));
bookModal.addEventListener('click', (e) => { if(e.target === bookModal) bookModal.classList.remove('active'); });

bookReserveForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        book_id: parseInt(document.getElementById('reserve-book-id').value),
        user_name: currentUser,
        booking_date: document.getElementById('reserve-date').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/books/reserve`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        if(response.ok) {
            const data = await response.json();
            alert(data.message);
            bookModal.classList.remove('active');
            bookReserveForm.reset();
            loadBooks();
        } else {
            const err = await response.json();
            alert("Error: " + err.detail);
        }
    } catch(e) {
        alert("Failed to submit reservation.");
    }
});

// ---- Student History Logic ----
async function loadUserHistory() {
    if (!currentUser) {
        const container = document.getElementById('history-container');
        container.innerHTML = '<div class="loading-state">Please login to view your booking history.</div>';
        return;
    }

    const container = document.getElementById('history-container');
    container.innerHTML = '<div class="loading-state">Fetching history for ' + currentUser + '...</div>';

    try {
        const response = await fetch(`${API_BASE}/user/${encodeURIComponent(currentUser)}/history`);
        const history = await response.json();
        
        container.innerHTML = '';
        if (history.length === 0) {
            container.innerHTML = '<div class="loading-state">No active or past bookings found for ' + currentUser + '.</div>';
            return;
        }

        history.forEach(item => {
            const card = document.createElement('div');
            card.className = 'resource-card';
            
            // Generate color based on status
            let badgeColor = 'var(--text-secondary)';
            if(item.status === 'pending' || item.status === 'pending pickup') badgeColor = 'var(--accent-orange)';
            else if(item.status === 'approved') badgeColor = 'var(--accent-green)';
            else if(item.status === 'rejected' || item.status === 'cancelled') badgeColor = 'var(--accent-red)';

            card.innerHTML = `
                <div class="resource-header">
                    <div>
                        <span class="resource-type">${item.category}</span>
                        <h3 class="resource-title">${item.item_name}</h3>
                    </div>
                    <span class="status-badge" style="background:${badgeColor}; color:#fff;">${item.status.toUpperCase()}</span>
                </div>
                <div class="resource-details" style="margin-top: 10px;">
                    <span>🕒 Start: ${item.start_time}</span>
                    <span>🛑 End: ${item.end_time}</span>
                </div>
                ${item.status !== 'cancelled' && item.status !== 'rejected' ? `
                    <div class="resource-actions" style="margin-top: auto;">
                        <button class="btn-primary btn-full" style="background: var(--accent-red);" 
                            onclick="cancelItemBooking(${item.booking_id}, '${item.category}')">Cancel</button>
                    </div>
                ` : '<div style="margin-top:auto"></div>'}
            `;
            container.appendChild(card);
        });
    } catch (error) {
        container.innerHTML = '<div class="loading-state">Failed to load history.</div>';
    }
}

async function cancelItemBooking(id, category) {
    if(!confirm(`Are you sure you want to cancel this ${category} reservation?`)) return;
    
    try {
        let url = `${API_BASE}/bookings/${id}`;
        if(category === 'Book') url = `${API_BASE}/books/reservations/${id}`;
        else if(category === 'Seat') url = `${API_BASE}/seats/bookings/${id}`;
        
        const response = await fetch(url, { method: 'DELETE' });
        if(response.ok) {
            alert("Cancellation successful.");
            loadUserHistory();
        } else {
            alert("Cancellation failed.");
        }
    } catch(e) {
        alert("Server error.");
    }
}


// ---- Admin Dashboard Logic ----
async function loadRequests() {
    const container = document.getElementById('requests-container');
    try {
        const response = await fetch(`${API_BASE}/admin/requests`);
        const requests = await response.json();
        
        container.innerHTML = '';
        if (requests.length === 0) {
            container.innerHTML = '<div class="loading-state">No pending requests!</div>';
            return;
        }

        requests.forEach(req => {
            const card = document.createElement('div');
            card.className = 'resource-card';
            card.innerHTML = `
                <div class="resource-header">
                    <h3 class="resource-title">${req.item_name}</h3>
                    <span class="status-badge" style="background:var(--accent-orange); color:#fff;">Pending ${req.category}</span>
                </div>
                <div class="resource-details">
                    <span>👤 Submitter: ${req.user_name}</span>
                    <span>🕒 Time: ${req.start_time} - ${req.end_time}</span>
                </div>
                <div class="resource-actions" style="display:flex; gap: 10px; margin-top: 10px;">
                    <button class="btn-primary" style="flex:1; background: var(--accent-green);" onclick="approveRequest(${req.id}, '${req.category}')">Approve</button>
                    <button class="btn-primary" style="flex:1; background: var(--primary);" onclick="rejectRequest(${req.id}, '${req.category}')">Reject</button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        container.innerHTML = '<div class="loading-state">Failed to load requests.</div>';
    }
}

async function approveRequest(id, category = 'Resource') {
    try {
        await fetch(`${API_BASE}/admin/requests/${id}/approve?category=${category}`, { method: 'POST' });
        loadRequests();
        loadResources();
        if(typeof loadSeats === 'function') loadSeats();
    } catch(e) { alert("Failed to approve"); }
}

async function rejectRequest(id, category = 'Resource') {
    try {
        await fetch(`${API_BASE}/admin/requests/${id}/reject?category=${category}`, { method: 'POST' });
        loadRequests();
    } catch(e) { alert("Failed to reject"); }
}

async function toggleResource(id) {
    try {
        await fetch(`${API_BASE}/admin/resources/${id}/toggle`, { method: 'PUT' });
        loadResources();
    } catch(e) { alert("Failed to toggle"); }
}

// ---- Multi-Model AI Insights Logic ----

function setupInsightListeners() {
    // Model A: Room
    const roomInputs = ['temp', 'light', 'sound', 'co2'];
    roomInputs.forEach(id => {
        document.getElementById(`slip-${id}`).addEventListener('input', (e) => {
            document.getElementById(`val-${id}`).textContent = e.target.value;
            fetchRoomPrediction();
        });
    });

    // Model B: Seat
    const seatInputs = ['hour', 'noise'];
    seatInputs.forEach(id => {
        document.getElementById(`slip-${id}`).addEventListener('input', (e) => {
            document.getElementById(`val-${id}`).textContent = e.target.value;
            fetchSeatPrediction();
        });
    });
    document.getElementById('slip-day').addEventListener('change', fetchSeatPrediction);

    // Model C: User
    const userInputs = ['duration', 'books', 'digital', 'logins'];
    userInputs.forEach(id => {
        document.getElementById(`slip-${id}`).addEventListener('input', (e) => {
            document.getElementById(`val-${id}`).textContent = e.target.value;
            fetchUserPrediction();
        });
    });
}

function triggerAllPredictions() {
    fetchRoomPrediction();
    fetchSeatPrediction();
    fetchUserPrediction();
}

async function fetchRoomPrediction() {
    const temp = document.getElementById('slip-temp').value;
    const light = document.getElementById('slip-light').value;
    const sound = document.getElementById('slip-sound').value;
    const co2 = document.getElementById('slip-co2').value;
    
    try {
        const res = await fetch(`${API_BASE}/predict/room?temp=${temp}&light=${light}&sound=${sound}&co2=${co2}`);
        const data = await res.json();
        document.getElementById('res-room').textContent = data.predicted_count;
    } catch(e) {
        document.getElementById('res-room').textContent = "Error";
    }
}

async function fetchSeatPrediction() {
    const hour = document.getElementById('slip-hour').value;
    const day = document.getElementById('slip-day').value;
    const noise = document.getElementById('slip-noise').value;
    
    try {
        const res = await fetch(`${API_BASE}/predict/seat?hour=${hour}&day_of_week=${day}&noise=${noise}`);
        const data = await res.json();
        document.getElementById('res-seat').textContent = data.occupied_probability + "%";
    } catch(e) {
        document.getElementById('res-seat').textContent = "Error";
    }
}

async function fetchUserPrediction() {
    const duration = document.getElementById('slip-duration').value;
    const books = document.getElementById('slip-books').value;
    const digital = document.getElementById('slip-digital').value;
    const logins = document.getElementById('slip-logins').value;
    
    try {
        const res = await fetch(`${API_BASE}/predict/satisfaction?duration=${duration}&books=${books}&digital=${digital}&logins=${logins}`);
        const data = await res.json();
        document.getElementById('res-user').textContent = data.predicted_satisfaction + " / 5";
    } catch(e) {
        document.getElementById('res-user').textContent = "Error";
    }
}

// ---- Library Optimizer Logic ----
async function loadOptimization() {
    const container = document.getElementById('optimizer-container');
    container.innerHTML = '<div class="loading-state">Fetching book inventory predictions...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/optimization/library`);
        const optimizations = await response.json();
        
        container.innerHTML = '';
        if(optimizations.length === 0) {
            container.innerHTML = '<div class="loading-state">No items calculated.</div>';
            return;
        }

        optimizations.forEach(opt => {
            const card = document.createElement('div');
            card.className = 'resource-card';
            
            let statusColor = 'var(--text-secondary)';
            if(opt.resource_status === 'Critical Shortage') statusColor = 'var(--accent-red)';
            else if(opt.resource_status === 'High Demand') statusColor = 'var(--accent-orange)';
            else if(opt.resource_status === 'Normal') statusColor = 'var(--accent-green)';
            
            card.innerHTML = `
                <div class="resource-header">
                    <div>
                        <h3 class="resource-title" style="white-space: normal; line-height: 1.2;">${opt.title.substring(0, 50)}${opt.title.length > 50 ? '...' : ''}</h3>
                        <span class="resource-type">📖 Book Analysis</span>
                    </div>
                    <span class="status-badge" style="background:${statusColor}; color:#fff;">${opt.resource_status}</span>
                </div>
                <div class="resource-details" style="margin-top: 10px;">
                    <span>Waitlist: ${opt.waitlist_count} | Available: ${opt.available_copies}/${opt.total_copies}</span>
                    <span>📊 Demand vs Supply: <strong>${opt.demand_ratio}%</strong></span>
                    <hr style="border-color: rgba(255,255,255,0.1); margin: 8px 0;">
                    <span>⏳ <strong>Loan Limit: ${opt.adjusted_loan_period}</strong></span>
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">${opt.justification}</span>
                    <br>
                    <span>🛒 Recommendation: <strong>${opt.acquisition_recommendation}</strong></span>
                </div>
                ${opt.alerts && opt.alerts !== 'None' ? `
                    <div style="margin-top: 10px; background: rgba(239, 68, 68, 0.1); border-left: 3px solid var(--accent-red); padding: 5px 10px; color: #fff; font-size: 0.85rem;">
                        ⚠️ ${opt.alerts}
                    </div>
                ` : ''}
            `;
            container.appendChild(card);
        });
    } catch (error) {
        container.innerHTML = '<div class="loading-state">Analysis Failed. Retry.</div>';
    }
}

// ---- Admin Auth Logic ----
const adminProfileBtn = document.getElementById('admin-profile-btn');
const userProfileText = document.getElementById('user-profile-text');
const loginModal = document.getElementById('login-modal');
const closeLoginModal = document.getElementById('close-login-modal');
const loginForm = document.getElementById('login-form');

// ---- Student Auth Logic ----
const studentLoginBtn = document.getElementById('student-login-btn');
const studentLoginModal = document.getElementById('student-login-modal');
const closeStudentLoginModal = document.getElementById('close-student-login-modal');
const studentLoginForm = document.getElementById('student-login-form');

function openStudentLoginModal() {
    studentLoginModal.classList.add('active');
}

studentLoginBtn.addEventListener('click', () => {
    if (currentUser) {
        // Logout
        currentUser = null;
        localStorage.removeItem('currentUser');
        updateUIForUser();
        alert("Student Logged Out.");
    } else {
        openStudentLoginModal();
    }
});

closeStudentLoginModal.addEventListener('click', () => studentLoginModal.classList.remove('active'));
studentLoginModal.addEventListener('click', (e) => { if(e.target === studentLoginModal) studentLoginModal.classList.remove('active'); });

studentLoginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const user = document.getElementById('student-user').value.trim();
    const pass = document.getElementById('student-pass').value;
    
    if (pass === "student123") {
        currentUser = user;
        localStorage.setItem('currentUser', user);
        updateUIForUser();
        studentLoginModal.classList.remove('active');
        studentLoginForm.reset();
        alert(`Welcome, ${user}! You can now book resources.`);
    } else {
        alert("Invalid student password. Use 'student123' for testing.");
    }
});

function updateUIForUser() {
    if (currentUser) {
        userProfileText.textContent = `Student: ${currentUser}`;
        studentLoginBtn.textContent = "Logout";
    } else {
        userProfileText.textContent = "Guest Mode";
        studentLoginBtn.textContent = "Student Login";
    }
    // Refresh history if active
    if (navs['nav-history'] && navs['nav-history'].classList.contains('active')) {
        loadUserHistory();
    }
}

// Global update on load
document.addEventListener('DOMContentLoaded', updateUIForUser);

adminProfileBtn.addEventListener('click', () => {
    if(isLoggedIn) {
        // Logout logic
        isLoggedIn = false;
        adminProfileBtn.textContent = "Admin Access";
        document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'none');
        // Re-render resources to hide buttons
        loadResources(); 
        
        // Kick them to dashboard if they were on requests page
        if(navs['nav-requests'] && navs['nav-requests'].classList.contains('active')) {
            document.getElementById('nav-dashboard').click();
        }
        alert("Admin Mode Disabled.");
    } else {
        loginModal.classList.add('active');
    }
});

closeLoginModal.addEventListener('click', () => loginModal.classList.remove('active'));
loginModal.addEventListener('click', (e) => { if(e.target === loginModal) loginModal.classList.remove('active'); });

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username: user, password: pass })
        });
        
        if(response.ok) {
            isLoggedIn = true;
            adminProfileBtn.textContent = "Exit Admin";
            loginModal.classList.remove('active');
            loginForm.reset();
            document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'block');
            loadResources(); // Re-render to show admin buttons
            alert("Login Successful! Admin privileges enabled.");
        } else {
            const err = await response.json();
            alert("Login Failed: " + err.detail);
        }
    } catch(e) {
         alert("Failed to connect to the server.");
    }
});
