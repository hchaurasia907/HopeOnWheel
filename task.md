# Flask Migration Tasks

- [ ] 1. Initialize Project Structure: Create `templates` and `static` (with `css`, `js`, `images`) directories.
- [ ] 2. Setup Database Schema: Create `models.py` with SQLAlchemy for Users, Providers, Hospitals, Doctors, and Bookings.
- [ ] 3. Implement Backend Application (`app.py`):
    - [ ] 3.1 Setup Flask app, DB config, and Secret Key.
    - [ ] 3.2 Implement Auth Routes (Login/Register for all roles).
    - [ ] 3.3 Implement Dashboard Routes (User, Provider, Hospital, Admin).
    - [ ] 3.4 Implement API Endpoints (Booking, Location Tracking, etc.).
- [x] 4. Develop Frontend Templates (`templates/`):
    - [x] 4.1 `base.html` (Master Layout)
    - [x] 4.2 `index.html` (Landing Page)
    - [x] 4.3 `auth.html` (Authentication portals)
    - [x] 4.4 `dashboard_user.html`
    - [x] 4.5 `dashboard_provider.html`
    - [x] 4.6 `dashboard_hospital.html`
    - [x] 4.7 `dashboard_admin.html`
- [x] 5. Implement Stunning Vanilla CSS (`static/css/style.css`): Apply modern aesthetics, glassmorphism, animations, and high-quality UI.
- [x] 6. Implement Interactivity (`static/js/main.js`): Setup Leaflet.js for interactive maps and dynamic AJAX queries.
- [x] 7. Perform Migration/Testing: Ensure the old workflows work equivalently in the new web app.
