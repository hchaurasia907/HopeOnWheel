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

MAPMYINDIA_API_KEY = "xznskzoivxovuionpicqjgydnaidvkulpuyb"

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
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        if action == 'register':
            if role == 'user':
                if User.query.filter_by(username=username).first():
                    flash('Username already exists!', 'error')
                else:
                    new_user = User(username=username, password=generate_password_hash(password))
                    db.session.add(new_user)
                    db.session.commit()
                    flash('User registered successfully!', 'success')
                    
            elif role == 'provider':
                name = request.form.get('name')
                ambulance_number = request.form.get('ambulance_number')
                service_type = request.form.get('service_type')
                
                if Provider.query.filter_by(username=username).first():
                    flash('Provider username already exists!', 'error')
                else:
                    new_provider = Provider(username=username, password=generate_password_hash(password), name=name, ambulance_number=ambulance_number, service_type=service_type)
                    db.session.add(new_provider)
                    db.session.commit()
                    flash('Provider registered successfully!', 'success')
                    
            elif role == 'hospital':
                name = request.form.get('name')
                location = request.form.get('location')
                
                if Hospital.query.filter_by(username=username).first():
                    flash('Hospital username already exists!', 'error')
                else:
                    new_hospital = Hospital(username=username, password=generate_password_hash(password), name=name, location=location)
                    db.session.add(new_hospital)
                    db.session.commit()
                    flash('Hospital registered successfully!', 'success')
                    
        elif action == 'login':
            user = None
            if role == 'user':
                user = User.query.filter_by(username=username).first()
            elif role == 'provider':
                user = Provider.query.filter_by(username=username).first()
            elif role == 'hospital':
                user = Hospital.query.filter_by(username=username).first()
            elif role == 'admin':
                user = Admin.query.filter_by(username=username).first()
                
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['user_type'] = role
                return redirect(url_for(f'{role}_dashboard'))
            else:
                flash('Invalid credentials!', 'error')
                
    return render_template('auth.html')

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
    return render_template('dashboard_admin.html', users=users, providers=providers, hospitals=hospitals, bookings=bookings)

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

@app.route('/api/update_booking_status', methods=['POST'])
def update_booking_status():
    provider = get_current_user()
    if not provider or session.get('user_type') != 'provider': return jsonify({"error": "Session expired or unauthorized. Please log in again."}), 401
    
    data = request.json
    booking = Booking.query.filter_by(tracking_id=data['tracking_id'], provider_name=provider.name).first()
    if not booking: return jsonify({"error": "Booking not found"}), 404
    
    booking.status = data['status']
    if booking.status == 'Completed':
        provider.wallet += 100.0  # Add standard payment to provider
    db.session.commit()
    
    return jsonify({"success": True})

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
    try:
        encoded_location = urllib.parse.quote(location)
        url = f"https://apis.mapmyindia.com/advancedmaps/v1/{MAPMYINDIA_API_KEY}/search?query={encoded_location}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get('results'):
                return jsonify(data['results'][0])
    except Exception as e:
        pass
    # Fallback to Delhi
    return jsonify({"lat": "28.6139", "lng": "77.2090"})

@app.route('/api/reverse_geocode', methods=['GET'])
def reverse_geocode():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    if not lat or not lng: return jsonify({"error": "Missing coordinates"}), 400
    
    try:
        url = f"https://apis.mapmyindia.com/advancedmaps/v1/{MAPMYINDIA_API_KEY}/rev_geocode?lat={lat}&lng={lng}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get('results'):
                return jsonify(data['results'][0])
    except Exception:
        pass
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
    
    try:
        # Hospitals Search
        h_url = f"https://apis.mapmyindia.com/advancedmaps/v1/{MAPMYINDIA_API_KEY}/nearby_search?keywords=hospital&refLocation={lat},{lng}&radius=75000"
        h_req = urllib.request.Request(h_url)
        with urllib.request.urlopen(h_req) as response:
            h_data = json.loads(response.read().decode())
            
        # Veterinary Search
        v_url = f"https://apis.mapmyindia.com/advancedmaps/v1/{MAPMYINDIA_API_KEY}/nearby_search?keywords=veterinary%20hospital&refLocation={lat},{lng}&radius=75000"
        v_req = urllib.request.Request(v_url)
        with urllib.request.urlopen(v_req) as response:
            v_data = json.loads(response.read().decode())
            
        return jsonify({
            "hospitals": h_data.get('results', []),
            "veterinary": v_data.get('results', [])
        })
    except Exception as e:
        pass
    
    return jsonify({"hospitals": [], "veterinary": []})

# Auto-initialize database on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Use environment port for Render compatibility
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
