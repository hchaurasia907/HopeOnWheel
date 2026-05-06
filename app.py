from http.client import UPGRADE_REQUIRED
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, Provider, Hospital, Doctor, Booking, HospitalAlert, HospitalNotification, Admin
import math
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import urllib.parse
import urllib.request
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-for-ambulance-app'
# Use an absolute path for SQLite to prevent issues on Windows
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ambulance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)




@app.before_request
def enforce_https():
    # Redirect HTTP to HTTPS in production environments
    if not app.debug and request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

@app.before_request
def create_tables():
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True
        
        # Initialize default admin if not exists
        if not Admin.query.filter_by(username='admin@123').first():
            admin = Admin(username='admin@123', password=generate_password_hash('Holon@123'))
            db.session.add(admin)
            db.session.commit()

def get_current_user():
    user_type = session.get('user_type')
    user_id = session.get('user_id')
    if not user_type or not user_id:
        return None
        
    if user_type == 'user':
        return User.query.get(user_id)
    elif user_type == 'provider':
        return Provider.query.get(user_id)
    elif user_type == 'hospital':
        return Hospital.query.get(user_id)
    elif user_type == 'admin':
        return Admin.query.get(user_id)
    return None

def haversine_distance(lat1, lng1, lat2, lng2):
    """Calculate distance in km between two GPS coordinates using Haversine formula."""
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLng = math.radians(lng2 - lng1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Live platform stats — real DB counts only."""
    total_bookings = Booking.query.count()
    completed_rides = Booking.query.filter_by(status='Completed').count()
    active_providers = Provider.query.count()
    hospitals_connected = Hospital.query.count()
    total_users = User.query.count()
    return jsonify({
        'bookings': total_bookings,
        'completed_rides': completed_rides,
        'providers': active_providers,
        'hospitals': hospitals_connected,
        'users': total_users
    })

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        action = request.form.get('action')
        role = request.form.get('role')
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        contact = request.form.get('contact', '').strip()
        
        if action == 'register':
            if not username or not password:
                flash('Username and password are required!', 'error')
                return render_template('auth.html')
            
            if not contact or len(contact) < 10:
                flash('Valid contact number (10+ digits) is required!', 'error')
                return render_template('auth.html')
            
            # Capitalize first letter of username
            username = username[0].upper() + username[1:] if len(username) > 0 else username
            
            try:
                if role == 'user':
                    # Case-insensitive username check
                    if User.query.filter(db.func.lower(User.username) == username.lower()).first():
                        flash('Username already taken! Choose another.', 'error')
                    elif User.query.filter_by(contact=contact).first():
                        flash('This contact number is already registered!', 'error')
                    else:
                        new_user = User(username=username, password=generate_password_hash(password), contact=contact)
                        db.session.add(new_user)
                        db.session.commit()
                        flash('User registered successfully! Please login.', 'success')
                        
                elif role == 'provider':
                    name = request.form.get('name', '').strip()
                    ambulance_number = request.form.get('ambulance_number', '').strip()
                    service_type = request.form.get('service_type')
                    
                    # Block Animal service type (Coming Soon)
                    if service_type == 'Animal':
                        flash('🐾 Animal Ambulance service is coming soon! Please register as Human Ambulance provider for now.', 'error')
                        return render_template('auth.html')
                    
                    # Capitalize name properly
                    name = name.title() if name else name
                    
                    if Provider.query.filter(db.func.lower(Provider.username) == username.lower()).first():
                        flash('Provider username already taken!', 'error')
                    elif Provider.query.filter_by(contact=contact).first():
                        flash('This contact number is already registered!', 'error')
                    else:
                        new_provider = Provider(username=username, password=generate_password_hash(password), contact=contact, name=name, ambulance_number=ambulance_number, service_type=service_type)
                        db.session.add(new_provider)
                        db.session.commit()
                        flash('Provider registered successfully! Please login.', 'success')
                        
                elif role == 'hospital':
                    name = request.form.get('name', '').strip()
                    location = request.form.get('location', '').strip()
                    
                    if not name:
                        flash('Hospital name is required!', 'error')
                        return render_template('auth.html')
                    
                    # Capitalize name properly
                    name = name.title() if name else name
                    
                    if Hospital.query.filter(db.func.lower(Hospital.username) == username.lower()).first():
                        flash('Hospital username already taken!', 'error')
                    elif Hospital.query.filter_by(contact=contact).first():
                        flash('This contact number is already registered!', 'error')
                    else:
                        hospital_lat = request.form.get('hospital_lat', type=float)
                        hospital_lng = request.form.get('hospital_lng', type=float)
                        new_hospital = Hospital(username=username, password=generate_password_hash(password), contact=contact, name=name, location=location, hospital_lat=hospital_lat, hospital_lng=hospital_lng)
                        db.session.add(new_hospital)
                        db.session.commit()
                        flash('Hospital registered successfully! Please login.', 'success')
            except Exception:
                db.session.rollback()
                flash('Username or contact number already exists! Please choose different ones.', 'error')
                    
        elif action == 'login':
            login_id = username  # Can be username or contact number
            user = None
            
            if role == 'user':
                user = User.query.filter(db.func.lower(User.username) == login_id.lower()).first() or User.query.filter_by(contact=login_id).first()
            elif role == 'provider':
                user = Provider.query.filter(db.func.lower(Provider.username) == login_id.lower()).first() or Provider.query.filter_by(contact=login_id).first()
            elif role == 'hospital':
                user = Hospital.query.filter(db.func.lower(Hospital.username) == login_id.lower()).first() or Hospital.query.filter_by(contact=login_id).first()
            elif role == 'admin':
                user = Admin.query.filter(db.func.lower(Admin.username) == login_id.lower()).first()
                
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['user_type'] = role
                return redirect(url_for(f'{role}_dashboard'))
            else:
                flash('Invalid credentials! Check your username/contact and password.', 'error')
                
    return render_template('auth.html')

@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    contact = data.get('contact', '').strip()
    new_password = data.get('new_password', '')
    role = data.get('role', 'user')
    
    if not contact or not new_password:
        return jsonify({"error": "Contact number and new password are required"}), 400
    
    if len(new_password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400
    
    user = None
    if role == 'user':
        user = User.query.filter_by(contact=contact).first()
    elif role == 'provider':
        user = Provider.query.filter_by(contact=contact).first()
    elif role == 'hospital':
        user = Hospital.query.filter_by(contact=contact).first()
    
    if not user:
        return jsonify({"error": "No account found with this contact number"}), 404
    
    user.password = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"success": True, "message": "Password reset successfully! You can now login with your new password."})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user_dashboard')
def user_dashboard():
    user = get_current_user()
    if session.get('user_type') != 'user': return redirect(url_for('auth'))
    bookings = Booking.query.filter_by(booked_by_username=user.username).all()
    providers = Provider.query.all()
    return render_template('dashboard_user.html', user=user, bookings=bookings, providers=providers)

@app.route('/provider_dashboard')
def provider_dashboard():
    provider = get_current_user()
    if session.get('user_type') != 'provider': return redirect(url_for('auth'))
    bookings = Booking.query.filter_by(provider_name=provider.name).all()
    return render_template('dashboard_provider.html', provider=provider, bookings=bookings)

@app.route('/hospital_dashboard')
def hospital_dashboard():
    hospital = get_current_user()
    if session.get('user_type') != 'hospital': return redirect(url_for('auth'))
    doctors = Doctor.query.filter_by(hospital_id=hospital.id).all()
    bookings = Booking.query.filter_by(status='Accepted').all()
    alerts = HospitalAlert.query.filter_by(hospital_id=hospital.id).order_by(HospitalAlert.created_at.desc()).limit(50).all()
    pending_alerts = HospitalAlert.query.filter_by(hospital_id=hospital.id, status='Incoming').count()
    # Direct user notifications
    direct_notifs = HospitalNotification.query.filter_by(hospital_id=hospital.id).order_by(HospitalNotification.created_at.desc()).limit(30).all()
    pending_notifs = HospitalNotification.query.filter_by(hospital_id=hospital.id, status='Pending').count()
    return render_template('dashboard_hospital.html', hospital=hospital, doctors=doctors, bookings=bookings, alerts=alerts, pending_alerts=pending_alerts, direct_notifs=direct_notifs, pending_notifs=pending_notifs)

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('user_type') != 'admin': return redirect(url_for('auth'))
    users = User.query.all()
    providers = Provider.query.all()
    hospitals = Hospital.query.all()
    bookings = Booking.query.all()
    doctors = Doctor.query.all()
    return render_template('dashboard_admin.html', users=users, providers=providers, hospitals=hospitals, bookings=bookings, doctors=doctors)

@app.route('/api/admin/delete_user/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    if session.get('user_type') != 'admin': return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(user_id)
    if not user: return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/admin/delete_provider/<int:provider_id>', methods=['DELETE'])
def admin_delete_provider(provider_id):
    if session.get('user_type') != 'admin': return jsonify({"error": "Unauthorized"}), 401
    provider = Provider.query.get(provider_id)
    if not provider: return jsonify({"error": "Provider not found"}), 404
    db.session.delete(provider)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/admin/delete_hospital/<int:hospital_id>', methods=['DELETE'])
def admin_delete_hospital(hospital_id):
    if session.get('user_type') != 'admin': return jsonify({"error": "Unauthorized"}), 401
    hospital = Hospital.query.get(hospital_id)
    if not hospital: return jsonify({"error": "Hospital not found"}), 404
    # Also delete associated doctors
    Doctor.query.filter_by(hospital_id=hospital_id).delete()
    db.session.delete(hospital)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/admin/delete_booking/<int:booking_id>', methods=['DELETE'])
def admin_delete_booking(booking_id):
    if session.get('user_type') != 'admin': return jsonify({"error": "Unauthorized"}), 401
    booking = Booking.query.get(booking_id)
    if not booking: return jsonify({"error": "Booking not found"}), 404
    db.session.delete(booking)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/book_ambulance', methods=['POST'])
def book_ambulance():
    user = get_current_user()
    if not user or session.get('user_type') != 'user': return jsonify({"error": "Session expired or unauthorized. Please log in again."}), 401
    
    data = request.json
    
    # Block Animal bookings (Coming Soon)
    if data.get('service_type') == 'Animal':
        return jsonify({"error": "🐾 Animal Ambulance is coming soon! This service is not available yet."}), 400
    
    provider = Provider.query.filter_by(name=data['provider_name']).first()
    if not provider: return jsonify({"error": "Provider not found"}), 404
    
    tracking_id = f"TRACK{Booking.query.count() + 1}"
    
    booking = Booking(
        tracking_id=tracking_id,
        provider_name=provider.name,
        ambulance_number=provider.ambulance_number,
        service_type=data['service_type'],
        booked_by_name=data['name'],
        booked_by_mobile=data['mobile'],
        booked_by_username=user.username,
        pickup_location=data['pickup_location'],
        pickup_lat=data.get('pickup_lat'),
        pickup_lng=data.get('pickup_lng')
    )
    db.session.add(booking)
    db.session.commit()
    
    # Hospital Connect: Notify nearby hospitals (within 20km)
    notified_count = 0
    pickup_lat = data.get('pickup_lat')
    pickup_lng = data.get('pickup_lng')
    if pickup_lat and pickup_lng:
        try:
            p_lat = float(pickup_lat)
            p_lng = float(pickup_lng)
            all_hospitals = Hospital.query.filter(
                Hospital.hospital_lat.isnot(None),
                Hospital.hospital_lng.isnot(None)
            ).all()
            for h in all_hospitals:
                dist = haversine_distance(p_lat, p_lng, h.hospital_lat, h.hospital_lng)
                if dist <= 20:
                    alert = HospitalAlert(
                        hospital_id=h.id,
                        booking_id=booking.id,
                        tracking_id=tracking_id,
                        patient_name=data['name'],
                        pickup_location=data['pickup_location'],
                        distance_km=round(dist, 1)
                    )
                    db.session.add(alert)
                    notified_count += 1
            db.session.commit()
        except Exception as e:
            print(f"Hospital alert error: {e}")
    
    return jsonify({"success": True, "tracking_id": tracking_id, "hospitals_notified": notified_count})

@app.route('/api/add_wallet', methods=['POST'])
def add_wallet():
    user = get_current_user()
    if not user or session.get('user_type') != 'user': return jsonify({"error": "Session expired or unauthorized. Please log in again."}), 401
    
    data = request.json
    amount = float(data.get('amount', 0))
    if amount <= 0: return jsonify({"error": "Amount must be positive"}), 400
    if amount > 50000: return jsonify({"error": "Maximum single top-up is ₹50,000"}), 400
    
    user.wallet += amount
    db.session.commit()
    return jsonify({"success": True, "new_balance": user.wallet})

@app.route('/api/update_booking_status', methods=['POST'])
def update_booking_status():
    provider = get_current_user()
    if not provider or session.get('user_type') != 'provider': return jsonify({"error": "Session expired or unauthorized. Please log in again."}), 401
    
    data = request.json
    booking = Booking.query.filter_by(tracking_id=data['tracking_id'], provider_name=provider.name).first()
    if not booking: return jsonify({"error": "Booking not found"}), 404
    
    booking.status = data['status']
    db.session.commit()
    
    return jsonify({"success": True})

@app.route('/api/pay_for_ride', methods=['POST'])
def pay_for_ride():
    user = get_current_user()
    if not user or session.get('user_type') != 'user': return jsonify({"error": "Session expired or unauthorized. Please log in again."}), 401
    
    data = request.json
    tracking_id = data.get('tracking_id')
    booking = Booking.query.filter_by(tracking_id=tracking_id, booked_by_username=user.username).first()
    if not booking: return jsonify({"error": "Booking not found"}), 404
    if booking.status != 'Completed': return jsonify({"error": "Ride is not completed yet"}), 400
    if booking.paid: return jsonify({"error": "Already paid"}), 400
    
    ride_cost = 100.0
    if user.wallet < ride_cost:
        return jsonify({"error": f"Insufficient balance. You need ₹{ride_cost} but have ₹{user.wallet:.2f}. Please add funds first."}), 400
    
    user.wallet -= ride_cost
    provider = Provider.query.filter_by(name=booking.provider_name).first()
    if provider:
        provider.wallet += ride_cost
    booking.paid = True
    db.session.commit()
    
    return jsonify({"success": True, "new_balance": user.wallet})

@app.route('/api/track_ambulance/<tracking_id>')
def track_ambulance(tracking_id):
    booking = Booking.query.filter_by(tracking_id=tracking_id).first()
    if not booking: return jsonify({"error": "Not found"}), 404
    
    provider = Provider.query.filter_by(name=booking.provider_name).first()
    if not provider: return jsonify({"error": "Ambulance provider records lost or deleted."}), 404
    return jsonify({
        "location": provider.current_location,
        "provider_lat": provider.provider_lat,
        "provider_lng": provider.provider_lng,
        "pickup_lat": booking.pickup_lat,
        "pickup_lng": booking.pickup_lng,
        "status": booking.status,
        "service_type": booking.service_type
    })

@app.route('/api/geocode', methods=['GET'])
def geocode():
    location = request.args.get('location')
    if not location:
        return jsonify({"lat": "28.6139", "lng": "77.2090"})
    try:
        encoded_location = urllib.parse.quote(location)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'HopeOnWheel/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data and len(data) > 0:
                return jsonify({"lat": data[0]["lat"], "lng": data[0]["lon"]})
    except Exception as e:
        print(f"Geocode error: {e}")
    return jsonify({"lat": "28.6139", "lng": "77.2090"})

@app.route('/api/reverse_geocode', methods=['GET'])
def reverse_geocode():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    if not lat or not lng: return jsonify({"error": "Missing coordinates"}), 400
    
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&addressdetails=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'HopeOnWheel/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get('display_name'):
                return jsonify({"formatted_address": data['display_name']})
    except Exception as e:
        print(f"Reverse geocode error: {e}")
    return jsonify({"formatted_address": f"GPS: {lat}, {lng}"})

@app.route('/api/add_doctor', methods=['POST'])
def add_doctor():
    hospital = get_current_user()
    if not hospital or session.get('user_type') != 'hospital': return jsonify({"error": "Session expired or unauthorized. Please log in again."}), 401
    
    data = request.json
    doctor_name = data.get('name')
    if not doctor_name: return jsonify({"error": "Doctor name is required"}), 400
    
    existing = Doctor.query.filter_by(name=doctor_name, hospital_id=hospital.id).first()
    if existing: return jsonify({"error": "Doctor already exists"}), 400
    
    new_doc = Doctor(name=doctor_name, hospital_id=hospital.id, available=True)
    db.session.add(new_doc)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/assign_doctor', methods=['POST'])
def assign_doctor():
    hospital = get_current_user()
    if not hospital or session.get('user_type') != 'hospital': return jsonify({"error": "Session expired or unauthorized. Please log in again."}), 401
    
    data = request.json
    tracking_id = data.get('tracking_id')
    doctor_name = data.get('doctor_name')
    
    doctor = Doctor.query.filter_by(name=doctor_name, hospital_id=hospital.id, available=True).first()
    if not doctor: return jsonify({"error": "Doctor not found or unavailable"}), 404
    
    booking = Booking.query.filter_by(tracking_id=tracking_id).first()
    if not booking: return jsonify({"error": "Booking not found"}), 404
    
    booking.assigned_doctor = doctor.name
    doctor.available = False
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/update_location', methods=['POST'])
def update_location():
    provider = get_current_user()
    if not provider or session.get('user_type') != 'provider': return jsonify({"error": "Session expired or unauthorized. Please log in again."}), 401
    
    data = request.json
    new_location = data.get('location')
    if not new_location: return jsonify({"error": "Location is required"}), 400
    
    provider.current_location = new_location
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/update_provider_gps', methods=['POST'])
def update_provider_gps():
    provider = get_current_user()
    if not provider or session.get('user_type') != 'provider': return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if 'lat' in data and 'lng' in data:
        provider.provider_lat = data['lat']
        provider.provider_lng = data['lng']
        provider.current_location = f"GPS: {data['lat']}, {data['lng']}"
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Missing GPS coordinates"}), 400

@app.route('/api/update_hospital_gps', methods=['POST'])
def update_hospital_gps():
    hospital = get_current_user()
    if not hospital or session.get('user_type') != 'hospital': return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if 'lat' in data and 'lng' in data:
        hospital.hospital_lat = data['lat']
        hospital.hospital_lng = data['lng']
        hospital.location = data.get('address', f"GPS: {data['lat']}, {data['lng']}")
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Missing GPS coordinates"}), 400

@app.route('/api/update_hospital_name', methods=['POST'])
def update_hospital_name():
    hospital = get_current_user()
    if not hospital or session.get('user_type') != 'hospital':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({"error": "Hospital name is required"}), 400
    
    # Title case the name
    hospital.name = name.title()
    db.session.commit()
    return jsonify({"success": True, "name": hospital.name})

@app.route('/api/registered_nearby_hospitals', methods=['GET'])
def registered_nearby_hospitals():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    if lat is None or lng is None:
        return jsonify({"error": "Missing coordinates"}), 400
    
    results = []
    all_hospitals = Hospital.query.filter(
        Hospital.hospital_lat.isnot(None),
        Hospital.hospital_lng.isnot(None)
    ).all()
    
    for h in all_hospitals:
        dist = haversine_distance(lat, lng, h.hospital_lat, h.hospital_lng)
        if dist <= 20:
            doctor_count = Doctor.query.filter_by(hospital_id=h.id).count()
            available_doctors = Doctor.query.filter_by(hospital_id=h.id, available=True).count()
            results.append({
                "id": h.id,
                "name": h.name,
                "location": h.location,
                "lat": h.hospital_lat,
                "lng": h.hospital_lng,
                "distance_km": round(dist, 1),
                "contact": h.contact,
                "doctors": doctor_count,
                "available_doctors": available_doctors,
                "registered": True
            })
    
    results.sort(key=lambda x: x['distance_km'])
    return jsonify({"hospitals": results})

@app.route('/api/hospital_alerts', methods=['GET'])
def get_hospital_alerts():
    hospital = get_current_user()
    if not hospital or session.get('user_type') != 'hospital':
        return jsonify({"error": "Unauthorized"}), 401
    
    alerts = HospitalAlert.query.filter_by(hospital_id=hospital.id).order_by(HospitalAlert.created_at.desc()).limit(30).all()
    result = []
    for a in alerts:
        booking = Booking.query.get(a.booking_id)
        result.append({
            "id": a.id,
            "tracking_id": a.tracking_id,
            "patient_name": a.patient_name,
            "pickup_location": a.pickup_location,
            "distance_km": a.distance_km,
            "status": a.status,
            "created_at": a.created_at.strftime("%d %b %Y, %I:%M %p") if a.created_at else "",
            "booking_status": booking.status if booking else "Unknown",
            "service_type": booking.service_type if booking else "",
            "ambulance": booking.ambulance_number if booking else ""
        })
    
    pending = sum(1 for a in alerts if a.status == 'Incoming')
    return jsonify({"alerts": result, "pending_count": pending})

@app.route('/api/hospital_alert_respond', methods=['POST'])
def hospital_alert_respond():
    hospital = get_current_user()
    if not hospital or session.get('user_type') != 'hospital':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    alert_id = data.get('alert_id')
    new_status = data.get('status')  # 'Ready' or 'Acknowledged'
    
    if new_status not in ('Ready', 'Acknowledged'):
        return jsonify({"error": "Invalid status"}), 400
    
    alert = HospitalAlert.query.filter_by(id=alert_id, hospital_id=hospital.id).first()
    if not alert:
        return jsonify({"error": "Alert not found"}), 404
    
    alert.status = new_status
    db.session.commit()
    return jsonify({"success": True, "new_status": new_status})

@app.route('/api/notify_hospital', methods=['POST'])
def notify_hospital():
    try:
        user = get_current_user()
        if not user or session.get('user_type') != 'user':
            return jsonify({"error": "Please login as a user"}), 401
        
        data = request.json
        if not data:
            return jsonify({"error": "No data received. Please try again."}), 400
        
        hospital_id = data.get('hospital_id')
        user_lat = data.get('lat')
        user_lng = data.get('lng')
        emergency_type = data.get('emergency_type', 'General')
        location_address = data.get('location_address', '')
        
        if not hospital_id:
            return jsonify({"error": "No hospital selected"}), 400
        if user_lat is None or user_lng is None:
            return jsonify({"error": "Your GPS location was not detected. Please allow location access and try again."}), 400
        
        hospital = Hospital.query.get(hospital_id)
        if not hospital:
            return jsonify({"error": "Hospital not found in our system"}), 404
        
        if hospital.hospital_lat is None or hospital.hospital_lng is None:
            return jsonify({"error": "This hospital has not set up its GPS location yet. Please try another hospital."}), 400
        
        # Check for recent duplicate notification (within 5 minutes)
        recent = HospitalNotification.query.filter_by(
            user_id=user.id, hospital_id=hospital_id, status='Pending'
        ).filter(HospitalNotification.created_at > datetime.utcnow() - timedelta(minutes=5)).first()
        if recent:
            return jsonify({"error": "You already notified this hospital. Please wait for their response."}), 400
        
        # Calculate distance and ETA
        dist = haversine_distance(float(user_lat), float(user_lng), float(hospital.hospital_lat), float(hospital.hospital_lng))
        eta = max(1, round(dist / 0.67))  # ~40 km/h average city speed
        
        notif = HospitalNotification(
            hospital_id=hospital_id,
            user_id=user.id,
            user_name=user.username,
            user_contact=user.contact or '',
            user_lat=float(user_lat),
            user_lng=float(user_lng),
            user_location_address=location_address or f"GPS: {float(user_lat):.4f}, {float(user_lng):.4f}",
            emergency_type=emergency_type,
            distance_km=round(dist, 1),
            eta_minutes=eta
        )
        db.session.add(notif)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "notification_id": notif.id,
            "hospital_name": hospital.name,
            "distance_km": round(dist, 1),
            "eta_minutes": eta
        })
    except Exception as e:
        db.session.rollback()
        print(f"Notify hospital error: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/user_notification_status', methods=['GET'])
def user_notification_status():
    user = get_current_user()
    if not user or session.get('user_type') != 'user':
        return jsonify({"error": "Unauthorized"}), 401
    
    notifs = HospitalNotification.query.filter_by(user_id=user.id).order_by(HospitalNotification.created_at.desc()).limit(10).all()
    result = []
    for n in notifs:
        hospital = Hospital.query.get(n.hospital_id)
        result.append({
            "id": n.id,
            "hospital_name": hospital.name if hospital else "Unknown",
            "hospital_location": hospital.location if hospital else "",
            "emergency_type": n.emergency_type,
            "distance_km": n.distance_km,
            "eta_minutes": n.eta_minutes,
            "status": n.status,
            "hospital_message": n.hospital_message,
            "created_at": n.created_at.strftime("%d %b, %I:%M %p") if n.created_at else ""
        })
    return jsonify({"notifications": result})

@app.route('/api/hospital_incoming_notifications', methods=['GET'])
def hospital_incoming_notifications():
    hospital = get_current_user()
    if not hospital or session.get('user_type') != 'hospital':
        return jsonify({"error": "Unauthorized"}), 401
    
    notifs = HospitalNotification.query.filter_by(hospital_id=hospital.id).order_by(HospitalNotification.created_at.desc()).limit(20).all()
    result = []
    for n in notifs:
        result.append({
            "id": n.id,
            "user_name": n.user_name,
            "user_contact": n.user_contact,
            "user_lat": n.user_lat,
            "user_lng": n.user_lng,
            "user_location_address": n.user_location_address,
            "emergency_type": n.emergency_type,
            "distance_km": n.distance_km,
            "eta_minutes": n.eta_minutes,
            "status": n.status,
            "created_at": n.created_at.strftime("%d %b %Y, %I:%M %p") if n.created_at else ""
        })
    pending = sum(1 for n in notifs if n.status == 'Pending')
    return jsonify({"notifications": result, "pending_count": pending})

@app.route('/api/hospital_notification_respond', methods=['POST'])
def hospital_notification_respond():
    hospital = get_current_user()
    if not hospital or session.get('user_type') != 'hospital':
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    notif_id = data.get('notification_id')
    new_status = data.get('status')  # 'Accepted' or 'Busy'
    message = data.get('message', '')
    
    if new_status not in ('Accepted', 'Busy'):
        return jsonify({"error": "Invalid status. Use 'Accepted' or 'Busy'"}), 400
    
    notif = HospitalNotification.query.filter_by(id=notif_id, hospital_id=hospital.id).first()
    if not notif:
        return jsonify({"error": "Notification not found"}), 404
    
    notif.status = new_status
    notif.hospital_message = message or ("Hospital is ready for your arrival" if new_status == 'Accepted' else "Hospital is currently busy")
    db.session.commit()
    return jsonify({"success": True, "new_status": new_status})

@app.route('/api/nearby_hospitals', methods=['GET'])
def nearby_hospitals():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    if not lat or not lng: return jsonify({"error": "Missing coordinates"}), 400
    
    hospitals = []
    veterinary = []
    
    try:
        # Search hospitals using Nominatim
        h_url = f"https://nominatim.openstreetmap.org/search?q=hospital+near+{lat},{lng}&format=json&limit=10&bounded=1&viewbox={float(lng)-0.15},{float(lat)+0.15},{float(lng)+0.15},{float(lat)-0.15}"
        h_req = urllib.request.Request(h_url, headers={'User-Agent': 'HopeOnWheel/1.0'})
        with urllib.request.urlopen(h_req, timeout=10) as response:
            h_data = json.loads(response.read().decode())
            for item in h_data:
                display = item.get("display_name", "")
                name_parts = [p.strip() for p in display.split(",")]
                short_name = ", ".join(name_parts[:3]) if len(name_parts) > 1 else display
                hospitals.append({
                    "name": short_name,
                    "lat": item.get("lat"),
                    "lng": item.get("lon"),
                    "full_address": display
                })
    except Exception as e:
        print(f"Hospital search error: {e}")
    
    try:
        # Search veterinary using Nominatim
        v_url = f"https://nominatim.openstreetmap.org/search?q=veterinary+near+{lat},{lng}&format=json&limit=10&bounded=1&viewbox={float(lng)-0.15},{float(lat)+0.15},{float(lng)+0.15},{float(lat)-0.15}"
        v_req = urllib.request.Request(v_url, headers={'User-Agent': 'HopeOnWheel/1.0'})
        with urllib.request.urlopen(v_req, timeout=10) as response:
            v_data = json.loads(response.read().decode())
            for item in v_data:
                display = item.get("display_name", "")
                name_parts = [p.strip() for p in display.split(",")]
                short_name = ", ".join(name_parts[:3]) if len(name_parts) > 1 else display
                veterinary.append({
                    "name": short_name,
                    "lat": item.get("lat"),
                    "lng": item.get("lon"),
                    "full_address": display
                })
    except Exception as e:
        print(f"Veterinary search error: {e}")
    
    return jsonify({"hospitals": hospitals, "veterinary": veterinary})

@app.route('/api/all_hospitals', methods=['GET'])
def all_hospitals():
    """Return ALL registered hospitals with GPS coordinates for the always-visible map."""
    results = []
    all_h = Hospital.query.filter(
        Hospital.hospital_lat.isnot(None),
        Hospital.hospital_lng.isnot(None)
    ).all()
    
    for h in all_h:
        doctor_count = Doctor.query.filter_by(hospital_id=h.id).count()
        available_doctors = Doctor.query.filter_by(hospital_id=h.id, available=True).count()
        results.append({
            "id": h.id,
            "name": h.name,
            "location": h.location,
            "lat": h.hospital_lat,
            "lng": h.hospital_lng,
            "contact": h.contact,
            "doctors": doctor_count,
            "available_doctors": available_doctors
        })
    
    return jsonify({"hospitals": results})

# Auto-initialize database on startup
with app.app_context():
    db.create_all()
    # Migrate: add hospital_lat/hospital_lng columns if missing
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()
    if 'hospital' in existing_tables:
        hospital_columns = [col['name'] for col in inspector.get_columns('hospital')]
        if 'hospital_lat' not in hospital_columns:
            db.session.execute(text('ALTER TABLE hospital ADD COLUMN hospital_lat FLOAT'))
        if 'hospital_lng' not in hospital_columns:
            db.session.execute(text('ALTER TABLE hospital ADD COLUMN hospital_lng FLOAT'))
    db.session.commit()

if __name__ == '__main__':
    # Use environment port for Render compatibility
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
