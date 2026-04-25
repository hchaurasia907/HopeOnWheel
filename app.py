from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, Provider, Hospital, Doctor, Booking, Admin
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

@app.route('/')
def index():
    return render_template('index.html')

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
                    
                    # Capitalize name properly
                    name = name.title() if name else name
                    
                    if Hospital.query.filter(db.func.lower(Hospital.username) == username.lower()).first():
                        flash('Hospital username already taken!', 'error')
                    elif Hospital.query.filter_by(contact=contact).first():
                        flash('This contact number is already registered!', 'error')
                    else:
                        new_hospital = Hospital(username=username, password=generate_password_hash(password), contact=contact, name=name, location=location)
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
    return render_template('dashboard_hospital.html', hospital=hospital, doctors=doctors, bookings=bookings)

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
    
    return jsonify({"success": True, "tracking_id": tracking_id})

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
                hospitals.append({"name": item.get("display_name", "").split(",")[0], "lat": item.get("lat"), "lng": item.get("lon")})
    except Exception as e:
        print(f"Hospital search error: {e}")
    
    try:
        # Search veterinary using Nominatim
        v_url = f"https://nominatim.openstreetmap.org/search?q=veterinary+near+{lat},{lng}&format=json&limit=10&bounded=1&viewbox={float(lng)-0.15},{float(lat)+0.15},{float(lng)+0.15},{float(lat)-0.15}"
        v_req = urllib.request.Request(v_url, headers={'User-Agent': 'HopeOnWheel/1.0'})
        with urllib.request.urlopen(v_req, timeout=10) as response:
            v_data = json.loads(response.read().decode())
            for item in v_data:
                veterinary.append({"name": item.get("display_name", "").split(",")[0], "lat": item.get("lat"), "lng": item.get("lon")})
    except Exception as e:
        print(f"Veterinary search error: {e}")
    
    return jsonify({"hospitals": hospitals, "veterinary": veterinary})

# Auto-initialize database on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Use environment port for Render compatibility
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
