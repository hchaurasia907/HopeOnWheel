import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.*;
import java.util.regex.*;
import java.util.List;
import java.io.*;
import java.net.*;
import java.awt.Desktop;
import java.net.URI;
import java.net.URLEncoder;
import org.json.simple.*;
import org.json.simple.parser.*;

class User {
    String username;
    String password;
    double wallet;

    User(String username, String password) {
        this.username = username;
        this.password = password;
        this.wallet = 0.0;
    }
}

class AmbulanceProvider {
    String username;
    String password;
    String name;
    String ambulanceNumber;
    String serviceType;
    double wallet;
    String currentLocation;

    AmbulanceProvider(String username, String password, String name, String ambulanceNumber, String serviceType) {
        this.username = username;
        this.password = password;
        this.name = name;
        this.ambulanceNumber = ambulanceNumber;
        this.serviceType = serviceType;
        this.wallet = 0.0;
        this.currentLocation = "Delhi, India"; // Default to Delhi
    }

    public void updateLocation(String location) {
        this.currentLocation = location;
    }

    public void manageBooking(AmbulanceBookingSystem system, String trackingId, boolean accept) {
        for (Booking booking : system.getBookings()) {
            if (booking.trackingId.equals(trackingId) && booking.ambulanceProviderName.equals(this.name)) {
                if (accept) {
                    booking.status = "Accepted";
                } else {
                    booking.status = "Rejected";
                }
                // Save bookings after status update
                system.saveBookings();
                return;
            }
        }
    }
}

class Hospital {
    String username;
    String password;
    String name;
    String location;
    double wallet;

    Hospital(String username, String password, String name, String location) {
        this.username = username;
        this.password = password;
        this.name = name;
        this.location = location;
        this.wallet = 0.0;
    }
}

class Doctor {
    String name;
    String hospitalName;
    boolean available;

    Doctor(String name, String hospitalName) {
        this.name = name;
        this.hospitalName = hospitalName;
        this.available = true;
    }
}

class Booking {
    String trackingId;
    String ambulanceProviderName;
    String ambulanceNumber;
    String type;
    String bookedByName;
    String bookedByMobile;
    String bookedByUsername;
    String pickupLocation;
    String status;
    String assignedDoctor;

    Booking(String trackingId, String ambulanceProviderName, String ambulanceNumber, String type, String bookedByName,
            String bookedByMobile, String bookedByUsername, String pickupLocation) {
        this.trackingId = trackingId;
        this.ambulanceProviderName = ambulanceProviderName;
        this.ambulanceNumber = ambulanceNumber;
        this.type = type;
        this.bookedByName = bookedByName;
        this.bookedByMobile = bookedByMobile;
        this.bookedByUsername = bookedByUsername;
        this.pickupLocation = pickupLocation;
        this.status = "Pending";
        this.assignedDoctor = null;
    }
}

class AmbulanceBookingSystem {
    private Map<String, User> users = new HashMap<>();
    private Map<String, User> admins = new HashMap<>();
    private Map<String, AmbulanceProvider> ambulanceProviders = new HashMap<>();
    private Map<String, Hospital> hospitals = new HashMap<>();
    private List<Doctor> doctors = new ArrayList<>();
    private List<Booking> bookings = new ArrayList<>();
    private int bookingCounter = 1;
    private static final String MAPMYINDIA_API_KEY = "xznskzoivxovuionpicqjgydnaidvkulpuyb";

    public AmbulanceBookingSystem() {
        admins.put("admin@123", new User("admin@123", "Holon@123"));
        loadAllData();
    }

    // Save and load methods for Users
    public void saveUsers() {
        JSONArray usersArray = new JSONArray();
        for (User user : users.values()) {
            JSONObject userObj = new JSONObject();
            userObj.put("username", user.username);
            userObj.put("password", user.password);
            userObj.put("wallet", user.wallet);
            usersArray.add(userObj);
        }
        try (FileWriter file = new FileWriter("users.json")) {
            file.write(usersArray.toJSONString());
            file.flush();
        } catch (IOException e) {
            JOptionPane.showMessageDialog(null, "Error saving users: " + e.getMessage());
        }
    }

    public void loadUsers() {
        File file = new File("users.json");
        if (!file.exists())
            return;
        JSONParser parser = new JSONParser();
        try (FileReader reader = new FileReader(file)) {
            JSONArray usersArray = (JSONArray) parser.parse(reader);
            for (Object obj : usersArray) {
                JSONObject userObj = (JSONObject) obj;
                String username = (String) userObj.get("username");
                String password = (String) userObj.get("password");
                double wallet = ((Number) userObj.get("wallet")).doubleValue();
                User user = new User(username, password);
                user.wallet = wallet;
                users.put(username, user);
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Error loading users: " + e.getMessage());
        }
    }

    // Save and load methods for Ambulance Providers
    public void saveProviders() {
        JSONArray providersArray = new JSONArray();
        for (AmbulanceProvider provider : ambulanceProviders.values()) {
            JSONObject providerObj = new JSONObject();
            providerObj.put("username", provider.username);
            providerObj.put("password", provider.password);
            providerObj.put("name", provider.name);
            providerObj.put("ambulanceNumber", provider.ambulanceNumber);
            providerObj.put("serviceType", provider.serviceType);
            providerObj.put("wallet", provider.wallet);
            providerObj.put("currentLocation", provider.currentLocation);
            providersArray.add(providerObj);
        }
        try (FileWriter file = new FileWriter("providers.json")) {
            file.write(providersArray.toJSONString());
            file.flush();
        } catch (IOException e) {
            JOptionPane.showMessageDialog(null, "Error saving providers: " + e.getMessage());
        }
    }

    public void loadProviders() {
        File file = new File("providers.json");
        if (!file.exists())
            return;
        JSONParser parser = new JSONParser();
        try (FileReader reader = new FileReader(file)) {
            JSONArray providersArray = (JSONArray) parser.parse(reader);
            for (Object obj : providersArray) {
                JSONObject providerObj = (JSONObject) obj;
                String username = (String) providerObj.get("username");
                String password = (String) providerObj.get("password");
                String name = (String) providerObj.get("name");
                String ambulanceNumber = (String) providerObj.get("ambulanceNumber");
                String serviceType = (String) providerObj.get("serviceType");
                double wallet = ((Number) providerObj.get("wallet")).doubleValue();
                String currentLocation = (String) providerObj.get("currentLocation");
                AmbulanceProvider provider = new AmbulanceProvider(username, password, name, ambulanceNumber,
                        serviceType);
                provider.wallet = wallet;
                provider.currentLocation = currentLocation != null ? currentLocation : "Delhi, India";
                ambulanceProviders.put(username, provider);
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Error loading providers: " + e.getMessage());
        }
    }

    // Save and load methods for Bookings
    public void saveBookings() {
        JSONArray bookingsArray = new JSONArray();
        for (Booking booking : bookings) {
            JSONObject bookingObj = new JSONObject();
            bookingObj.put("trackingId", booking.trackingId);
            bookingObj.put("ambulanceProviderName", booking.ambulanceProviderName);
            bookingObj.put("ambulanceNumber", booking.ambulanceNumber);
            bookingObj.put("type", booking.type);
            bookingObj.put("bookedByName", booking.bookedByName);
            bookingObj.put("bookedByMobile", booking.bookedByMobile);
            bookingObj.put("bookedByUsername", booking.bookedByUsername);
            bookingObj.put("pickupLocation", booking.pickupLocation);
            bookingObj.put("status", booking.status);
            bookingObj.put("assignedDoctor", booking.assignedDoctor);
            bookingsArray.add(bookingObj);
        }
        try (FileWriter file = new FileWriter("bookings.json")) {
            file.write(bookingsArray.toJSONString());
            file.flush();
        } catch (IOException e) {
            JOptionPane.showMessageDialog(null, "Error saving bookings: " + e.getMessage());
        }
    }

    public void loadBookings() {
        File file = new File("bookings.json");
        if (!file.exists())
            return;
        JSONParser parser = new JSONParser();
        try (FileReader reader = new FileReader(file)) {
            JSONArray bookingsArray = (JSONArray) parser.parse(reader);
            for (Object obj : bookingsArray) {
                JSONObject bookingObj = (JSONObject) obj;
                String trackingId = (String) bookingObj.get("trackingId");
                String ambulanceProviderName = (String) bookingObj.get("ambulanceProviderName");
                String ambulanceNumber = (String) bookingObj.get("ambulanceNumber");
                String type = (String) bookingObj.get("type");
                String bookedByName = (String) bookingObj.get("bookedByName");
                String bookedByMobile = (String) bookingObj.get("bookedByMobile");
                String bookedByUsername = (String) bookingObj.get("bookedByUsername");
                String pickupLocation = (String) bookingObj.get("pickupLocation");
                String status = (String) bookingObj.get("status");
                String assignedDoctor = (String) bookingObj.get("assignedDoctor");
                Booking booking = new Booking(trackingId, ambulanceProviderName, ambulanceNumber, type, bookedByName,
                        bookedByMobile, bookedByUsername, pickupLocation != null ? pickupLocation : "Delhi, India");
                booking.status = status;
                booking.assignedDoctor = assignedDoctor;
                bookings.add(booking);
                // Update bookingCounter to avoid duplicate tracking IDs
                try {
                    int num = Integer.parseInt(trackingId.replace("TRACK", ""));
                    if (num >= bookingCounter) {
                        bookingCounter = num + 1;
                    }
                } catch (NumberFormatException ignored) {
                }
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Error loading bookings: " + e.getMessage());
        }
    }

    // Save and load methods for Hospitals
    public void saveHospitals() {
        JSONArray hospitalsArray = new JSONArray();
        for (Hospital hospital : hospitals.values()) {
            JSONObject hospitalObj = new JSONObject();
            hospitalObj.put("username", hospital.username);
            hospitalObj.put("password", hospital.password);
            hospitalObj.put("name", hospital.name);
            hospitalObj.put("location", hospital.location);
            hospitalObj.put("wallet", hospital.wallet);
            hospitalsArray.add(hospitalObj);
        }
        try (FileWriter file = new FileWriter("hospitals.json")) {
            file.write(hospitalsArray.toJSONString());
            file.flush();
        } catch (IOException e) {
            JOptionPane.showMessageDialog(null, "Error saving hospitals: " + e.getMessage());
        }
    }

    public void loadHospitals() {
        File file = new File("hospitals.json");
        if (!file.exists())
            return;
        JSONParser parser = new JSONParser();
        try (FileReader reader = new FileReader(file)) {
            JSONArray hospitalsArray = (JSONArray) parser.parse(reader);
            for (Object obj : hospitalsArray) {
                JSONObject hospitalObj = (JSONObject) obj;
                String username = (String) hospitalObj.get("username");
                String password = (String) hospitalObj.get("password");
                String name = (String) hospitalObj.get("name");
                String location = (String) hospitalObj.get("location");
                double wallet = ((Number) hospitalObj.get("wallet")).doubleValue();
                Hospital hospital = new Hospital(username, password, name, location);
                hospital.wallet = wallet;
                hospitals.put(username, hospital);
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Error loading hospitals: " + e.getMessage());
        }
    }

    // Save and load methods for Doctors
    public void saveDoctors() {
        JSONArray doctorsArray = new JSONArray();
        for (Doctor doctor : doctors) {
            JSONObject doctorObj = new JSONObject();
            doctorObj.put("name", doctor.name);
            doctorObj.put("hospitalName", doctor.hospitalName);
            doctorObj.put("available", doctor.available);
            doctorsArray.add(doctorObj);
        }
        try (FileWriter file = new FileWriter("doctors.json")) {
            file.write(doctorsArray.toJSONString());
            file.flush();
        } catch (IOException e) {
            JOptionPane.showMessageDialog(null, "Error saving doctors: " + e.getMessage());
        }
    }

    public void loadDoctors() {
        File file = new File("doctors.json");
        if (!file.exists())
            return;
        JSONParser parser = new JSONParser();
        try (FileReader reader = new FileReader(file)) {
            JSONArray doctorsArray = (JSONArray) parser.parse(reader);
            for (Object obj : doctorsArray) {
                JSONObject doctorObj = (JSONObject) obj;
                String name = (String) doctorObj.get("name");
                String hospitalName = (String) doctorObj.get("hospitalName");
                boolean available = (Boolean) doctorObj.get("available");
                Doctor doctor = new Doctor(name, hospitalName);
                doctor.available = available;
                doctors.add(doctor);
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Error loading doctors: " + e.getMessage());
        }
    }

    // Save all data
    public void saveAllData() {
        saveUsers();
        saveProviders();
        saveHospitals();
        saveDoctors();
        saveBookings();
        JOptionPane.showMessageDialog(null, "All data saved successfully.");
    }

    // Load all data
    public void loadAllData() {
        loadUsers();
        loadProviders();
        loadHospitals();
        loadDoctors();
        loadBookings();
    }

    public Map<String, User> getUsers() {
        return users;
    }

    public boolean registerUser(String username, String password) {
        if (!isValidUsername(username)) {
            JOptionPane.showMessageDialog(null,
                    "Invalid username! It must be at least 3 characters long and alphanumeric.");
            return false;
        }
        if (users.containsKey(username)) {
            JOptionPane.showMessageDialog(null, "Username already exists!");
            return false;
        }
        if (!isValidPassword(password)) {
            JOptionPane.showMessageDialog(null,
                    "Invalid password! It must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.");
            return false;
        }

        users.put(username, new User(username, password));
        saveUsers(); // Save to JSON file after registration
        JOptionPane.showMessageDialog(null, "User registered successfully!");
        return true;
    }

    public User loginUser(String username, String password) {
        User user = users.get(username);
        if (user == null) {
            JOptionPane.showMessageDialog(null, "Invalid username!");
            return null;
        }
        if (!user.password.equals(password)) {
            JOptionPane.showMessageDialog(null, "Invalid password!");
            return null;
        }
        JOptionPane.showMessageDialog(null, "User login successful!");
        return user;
    }

    public boolean registerAmbulanceProvider(String username, String password, String name, String ambulanceNumber,
            String serviceType) {
        if (!isValidUsername(username)) {
            JOptionPane.showMessageDialog(null,
                    "Invalid username! It must be at least 3 characters long and alphanumeric.");
            return false;
        }
        if (ambulanceProviders.containsKey(username)) {
            JOptionPane.showMessageDialog(null, "Ambulance provider username already exists!");
            return false;
        }
        if (!isValidPassword(password)) {
            JOptionPane.showMessageDialog(null,
                    "Invalid password! It must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.");
            return false;
        }

        ambulanceProviders.put(username, new AmbulanceProvider(username, password, name, ambulanceNumber, serviceType));
        saveProviders(); // Save to JSON file after registration
        JOptionPane.showMessageDialog(null, "Ambulance provider registered successfully!");
        return true;
    }

    public boolean registerHospital(String username, String password, String name, String location) {
        if (!isValidUsername(username)) {
            JOptionPane.showMessageDialog(null,
                    "Invalid username! It must be at least 3 characters long and alphanumeric.");
            return false;
        }
        if (hospitals.containsKey(username)) {
            JOptionPane.showMessageDialog(null, "Hospital username already exists!");
            return false;
        }
        if (!isValidPassword(password)) {
            JOptionPane.showMessageDialog(null,
                    "Invalid password! It must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.");
            return false;
        }

        hospitals.put(username, new Hospital(username, password, name, location));
        saveHospitals(); // Save to JSON file after registration
        JOptionPane.showMessageDialog(null, "Hospital registered successfully!");
        return true;
    }

    public Hospital loginHospital(String username, String password) {
        Hospital hospital = hospitals.get(username);
        if (hospital == null) {
            JOptionPane.showMessageDialog(null, "Invalid hospital username!");
            return null;
        }
        if (!hospital.password.equals(password)) {
            JOptionPane.showMessageDialog(null, "Invalid password!");
            return null;
        }
        JOptionPane.showMessageDialog(null, "Hospital login successful!");
        return hospital;
    }

    public boolean addDoctor(String doctorName, String hospitalName) {
        // Check if hospital exists
        Hospital hospital = hospitals.values().stream()
                .filter(h -> h.name.equalsIgnoreCase(hospitalName))
                .findFirst()
                .orElse(null);
        if (hospital == null) {
            JOptionPane.showMessageDialog(null, "Hospital not found!");
            return false;
        }

        // Check if doctor already exists
        for (Doctor doctor : doctors) {
            if (doctor.name.equalsIgnoreCase(doctorName) && doctor.hospitalName.equalsIgnoreCase(hospitalName)) {
                JOptionPane.showMessageDialog(null, "Doctor already exists for this hospital!");
                return false;
            }
        }

        doctors.add(new Doctor(doctorName, hospitalName));
        saveDoctors();
        JOptionPane.showMessageDialog(null, "Doctor added successfully!");
        return true;
    }

    public List<Doctor> getDoctorsByHospital(String hospitalName) {
        List<Doctor> hospitalDoctors = new ArrayList<>();
        for (Doctor doctor : doctors) {
            if (doctor.hospitalName.equalsIgnoreCase(hospitalName)) {
                hospitalDoctors.add(doctor);
            }
        }
        return hospitalDoctors;
    }

    public String[] getAvailableDoctorsByHospital(String hospitalName) {
        List<String> availableDoctors = new ArrayList<>();
        for (Doctor doctor : doctors) {
            if (doctor.hospitalName.equalsIgnoreCase(hospitalName) && doctor.available) {
                availableDoctors.add(doctor.name);
            }
        }
        return availableDoctors.toArray(new String[0]);
    }

    public boolean assignDoctorToBooking(String trackingId, String doctorName) {
        for (Booking booking : bookings) {
            if (booking.trackingId.equals(trackingId)) {
                // Check if doctor exists and is available
                Doctor doctor = doctors.stream()
                        .filter(d -> d.name.equals(doctorName) && d.available)
                        .findFirst()
                        .orElse(null);
                if (doctor == null) {
                    JOptionPane.showMessageDialog(null, "Doctor not available!");
                    return false;
                }

                booking.assignedDoctor = doctorName;
                doctor.available = false;
                saveBookings();
                saveDoctors();
                JOptionPane.showMessageDialog(null, "Doctor assigned successfully to booking!");
                return true;
            }
        }
        JOptionPane.showMessageDialog(null, "Booking not found!");
        return false;
    }

    public String[] getHospitalBookings(String hospitalName) {
        List<String> hospitalBookings = new ArrayList<>();
        for (Booking booking : bookings) {
            if (booking.status.equals("Accepted")
                    && (booking.assignedDoctor == null || booking.assignedDoctor.isEmpty())) {
                hospitalBookings.add("ID: " + booking.trackingId + " | Patient: " + booking.bookedByName +
                        " | Mobile: " + booking.bookedByMobile + " | Location: " + booking.pickupLocation +
                        " | Doctor: Not Assigned");
            }
        }
        return hospitalBookings.toArray(new String[0]);
    }

    public AmbulanceProvider loginAmbulanceProvider(String username, String password) {
        AmbulanceProvider provider = ambulanceProviders.get(username);
        if (provider == null) {
            JOptionPane.showMessageDialog(null, "Invalid ambulance provider username!");
            return null;
        }
        if (!provider.password.equals(password)) {
            JOptionPane.showMessageDialog(null, "Invalid password!");
            return null;
        }
        JOptionPane.showMessageDialog(null, "Ambulance provider login successful!");
        return provider;
    }

    public User loginAdmin(String username, String password) {
        User admin = admins.get(username);
        if (admin == null) {
            JOptionPane.showMessageDialog(null, "Invalid admin username!");
            return null;
        }
        if (!admin.password.equals(password)) {
            JOptionPane.showMessageDialog(null, "Invalid password!");
            return null;
        }
        JOptionPane.showMessageDialog(null, "Admin login successful!");
        return admin;
    }

    public String[] getAmbulanceProviders() {
        String[] providers = new String[ambulanceProviders.size()];
        int i = 0;
        for (AmbulanceProvider provider : ambulanceProviders.values()) {
            providers[i++] = provider.name + " (" + provider.serviceType + ") - " + provider.ambulanceNumber;
        }
        return providers;
    }

    public String[] getAmbulanceProvidersByType(String serviceType) {
        List<String> filteredProviders = new ArrayList<>();
        for (AmbulanceProvider provider : ambulanceProviders.values()) {
            if (provider.serviceType.equalsIgnoreCase(serviceType)) {
                filteredProviders.add(provider.name + " (" + provider.serviceType + ") - " + provider.ambulanceNumber);
            }
        }
        return filteredProviders.toArray(new String[0]);
    }

    public String bookAmbulance(User user, String type, String bookedByName, String bookedByMobile, String providerName,
            String pickupLocation) {
        if (!isValidPhoneNumber(bookedByMobile)) {
            JOptionPane.showMessageDialog(null, "Invalid phone number! It must be 10 digits long.");
            return null;
        }

        // Extract provider name before the "("
        String providerNameOnly = providerName.contains("(")
                ? providerName.substring(0, providerName.indexOf("(")).trim()
                : providerName.split(" ")[0];

        AmbulanceProvider provider = ambulanceProviders.values().stream()
                .filter(p -> p.name.equalsIgnoreCase(providerNameOnly))
                .findFirst()
                .orElse(null);

        if (provider == null) {
            JOptionPane.showMessageDialog(null, "Ambulance provider not found!");
            return null;
        }

        String trackingId = "TRACK" + bookingCounter++;
        bookings.add(new Booking(trackingId, provider.name, provider.ambulanceNumber, type, bookedByName,
                bookedByMobile, user.username, pickupLocation));
        saveBookings(); // Save to JSON file after booking
        return trackingId;
    }

    public String[] getAllBookings() {
        String[] bookingList = new String[bookings.size()];
        for (int i = 0; i < bookings.size(); i++) {
            Booking b = bookings.get(i);
            bookingList[i] = "ID: " + b.trackingId + " | Provider: " + b.ambulanceProviderName +
                    " | Type: " + b.type + " | Status: " + b.status;
        }
        return bookingList;
    }

    public String[] getProviderBookings(String providerName) {
        List<String> providerBookings = new ArrayList<>();
        for (Booking booking : bookings) {
            if (booking.ambulanceProviderName.equalsIgnoreCase(providerName)) {
                providerBookings.add("ID: " + booking.trackingId + " | Type: " + booking.type +
                        " | Booked By: " + booking.bookedByName + " | Status: " + booking.status);
            }
        }
        return providerBookings.toArray(new String[0]);
    }

    public String[] getUserBookings(String username) {
        List<String> userBookings = new ArrayList<>();
        for (Booking booking : bookings) {
            if (booking.bookedByUsername.equals(username)) {
                userBookings.add("ID: " + booking.trackingId + " | Provider: " + booking.ambulanceProviderName +
                        " | Type: " + booking.type + " | Status: " + booking.status);
            }
        }
        return userBookings.toArray(new String[0]);
    }

    public boolean completeRide(AmbulanceProvider provider, String trackingId) {
        for (Booking booking : bookings) {
            if (booking.trackingId.equals(trackingId) && booking.ambulanceProviderName.equals(provider.name)
                    && booking.status.equals("Accepted")) {
                double payment = 100.0;
                provider.wallet += payment;
                booking.status = "Completed";
                saveProviders(); // Save providers after wallet update
                saveBookings(); // Save bookings after status update
                return true;
            }
        }
        return false;
    }

    public void addToWallet(User user, double amount) {
        user.wallet += amount;
    }

    public List<Booking> getBookings() {
        return bookings;
    }

    private boolean isValidUsername(String username) {
        return username.matches("^[a-zA-Z0-9]{3,}$");
    }

    private boolean isValidPassword(String password) {
        if (password.length() < 8) {
            return false;
        }

        boolean hasUpper = false;
        boolean hasLower = false;
        boolean hasDigit = false;
        boolean hasSpecial = false;

        for (char c : password.toCharArray()) {
            if (Character.isUpperCase(c))
                hasUpper = true;
            else if (Character.isLowerCase(c))
                hasLower = true;
            else if (Character.isDigit(c))
                hasDigit = true;
            else
                hasSpecial = true;
        }

        return hasUpper && hasLower && hasDigit && hasSpecial;
    }

    private boolean isValidPhoneNumber(String phoneNumber) {
        return phoneNumber.matches("\\d{10}");
    }

    public String trackAmbulance(String trackingId) {
        for (Booking booking : bookings) {
            if (booking.trackingId.equals(trackingId)) {
                AmbulanceProvider provider = ambulanceProviders.values().stream()
                        .filter(p -> p.name.equals(booking.ambulanceProviderName))
                        .findFirst().orElse(null);
                if (provider != null) {
                    return provider.currentLocation;
                }
            }
        }
        return "Booking not found or provider not available";
    }

    public double[] geocodeLocation(String location) {
        try {
            String encodedLocation = URLEncoder.encode(location, "UTF-8");
            String url = "https://apis.mapmyindia.com/advancedmaps/v1/" + MAPMYINDIA_API_KEY + "/search?query="
                    + encodedLocation;
            HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
            conn.setRequestMethod("GET");
            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            JSONParser parser = new JSONParser();
            JSONObject jsonResponse = (JSONObject) parser.parse(response.toString());
            JSONArray results = (JSONArray) jsonResponse.get("results");
            if (results != null && !results.isEmpty()) {
                JSONObject firstResult = (JSONObject) results.get(0);
                double lat = ((Number) firstResult.get("lat")).doubleValue();
                double lng = ((Number) firstResult.get("lng")).doubleValue();
                return new double[] { lat, lng };
            }
            return new double[] { 28.6139, 77.2090 }; // Default to Delhi if geocoding fails
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "Error geocoding location: " + e.getMessage());
            return new double[] { 28.6139, 77.2090 }; // Fallback to Delhi
        }
    }

    public String getNearestHospital(double lat, double lng) {
        try {
            String url = "https://apis.mapmyindia.com/advancedmaps/v1/" + MAPMYINDIA_API_KEY
                    + "/nearby_search?keywords=hospital&refLocation=" + lat + "," + lng + "&radius=75000";
            HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
            conn.setRequestMethod("GET");
            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            JSONParser parser = new JSONParser();
            JSONObject jsonResponse = (JSONObject) parser.parse(response.toString());
            JSONArray results = (JSONArray) jsonResponse.get("results");
            if (results != null && !results.isEmpty()) {
                JSONObject firstResult = (JSONObject) results.get(0);
                return (String) firstResult.get("name");
            }
            return "No hospitals found nearby";
        } catch (Exception e) {
            return "Error fetching nearest hospital: " + e.getMessage();
        }
    }

    public String getNearestVeterinary(double lat, double lng) {
        try {
            String url = "https://apis.mapmyindia.com/advancedmaps/v1/" + MAPMYINDIA_API_KEY
                    + "/nearby_search?keywords=veterinary%20hospital&refLocation=" + lat + "," + lng + "&radius=75000";
            HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
            conn.setRequestMethod("GET");
            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();

            JSONParser parser = new JSONParser();
            JSONObject jsonResponse = (JSONObject) parser.parse(response.toString());
            JSONArray results = (JSONArray) jsonResponse.get("results");
            if (results != null && !results.isEmpty()) {
                JSONObject firstResult = (JSONObject) results.get(0);
                return (String) firstResult.get("name");
            }
            return "No veterinary hospitals found nearby";
        } catch (Exception e) {
            return "Error fetching nearest veterinary hospital: " + e.getMessage();
        }
    }

    public String getNearbyHospitals(double lat, double lng) {
        try {
            String url = "https://apis.mapmyindia.com/advancedmaps/v1/" + MAPMYINDIA_API_KEY
                    + "/nearby_search?keywords=hospital&refLocation=" + lat + "," + lng + "&radius=75000";
            HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
            conn.setRequestMethod("GET");
            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();
            return response.toString();
        } catch (Exception e) {
            return "Error fetching hospitals: " + e.getMessage();
        }
    }

    public String getTrafficData(double startLat, double startLng, double endLat, double endLng) {
        try {
            String url = "https://apis.mapmyindia.com/advancedmaps/v1/" + MAPMYINDIA_API_KEY + "/route?start="
                    + startLat + "," + startLng + "&destination=" + endLat + "," + endLng
                    + "&alternatives=false&with_traffic=true";
            HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
            conn.setRequestMethod("GET");
            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String inputLine;
            StringBuilder response = new StringBuilder();
            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();
            return response.toString();
        } catch (Exception e) {
            return "Error fetching traffic data: " + e.getMessage();
        }
    }
}

public class AmbulanceBookingGUI {
    private AmbulanceBookingSystem system;
    private JFrame frame;
    private CardLayout cardLayout;
    private JPanel cardPanel;
    private User currentUser;
    private AmbulanceProvider currentProvider;
    private Hospital currentHospital;
    private JComboBox<String> arrangeDoctorBookingCombo;

    public AmbulanceBookingGUI() {
        system = new AmbulanceBookingSystem();
        initializeGUI();
    }

    private void initializeGUI() {
        frame = new JFrame("Ambulance Booking System");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(800, 600);
        frame.setLocationRelativeTo(null);

        cardLayout = new CardLayout();
        cardPanel = new JPanel(cardLayout);

        createMainMenu();
        createUserRegistration();
        createUserLogin();
        createAdminLogin();
        createProviderRegistration();
        createProviderLogin();
        createHospitalRegistration();
        createHospitalLogin();
        createUserMenu();
        createAdminMenu();
        createProviderMenu();
        createHospitalMenu();
        createBookingPanel();
        createWalletPanel();
        createAddDoctorPanel();
        createArrangeDoctorPanel();

        // Populate arrange doctor combo after initialization
        if (arrangeDoctorBookingCombo != null) {
            arrangeDoctorBookingCombo.removeAllItems();
        }

        frame.add(cardPanel);
        frame.setVisible(true);
    }

    private void createMainMenu() {
        JPanel panel = new JPanel(new GridLayout(8, 1, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JButton userRegBtn = new JButton("User Registration");
        JButton userLoginBtn = new JButton("User Login");
        JButton adminLoginBtn = new JButton("Admin Login");
        JButton providerRegBtn = new JButton("Provider Registration");
        JButton providerLoginBtn = new JButton("Provider Login");
        JButton hospitalRegBtn = new JButton("Hospital Registration");
        JButton hospitalLoginBtn = new JButton("Hospital Login");
        JButton exitBtn = new JButton("Exit");

        userRegBtn.addActionListener(e -> cardLayout.show(cardPanel, "UserRegistration"));
        userLoginBtn.addActionListener(e -> cardLayout.show(cardPanel, "UserLogin"));
        adminLoginBtn.addActionListener(e -> cardLayout.show(cardPanel, "AdminLogin"));
        providerRegBtn.addActionListener(e -> cardLayout.show(cardPanel, "ProviderRegistration"));
        providerLoginBtn.addActionListener(e -> cardLayout.show(cardPanel, "ProviderLogin"));
        hospitalRegBtn.addActionListener(e -> cardLayout.show(cardPanel, "HospitalRegistration"));
        hospitalLoginBtn.addActionListener(e -> cardLayout.show(cardPanel, "HospitalLogin"));
        exitBtn.addActionListener(e -> System.exit(0));

        panel.add(userRegBtn);
        panel.add(userLoginBtn);
        panel.add(adminLoginBtn);
        panel.add(providerRegBtn);
        panel.add(providerLoginBtn);
        panel.add(hospitalRegBtn);
        panel.add(hospitalLoginBtn);
        panel.add(exitBtn);

        cardPanel.add(panel, "MainMenu");
    }

    private void createUserRegistration() {
        JPanel panel = new JPanel(new GridLayout(4, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel userLabel = new JLabel("Username:");
        JTextField userField = new JTextField();
        JLabel passLabel = new JLabel("Password:");
        JPasswordField passField = new JPasswordField();
        JButton registerBtn = new JButton("Register");
        JButton backBtn = new JButton("Back");

        registerBtn.addActionListener(e -> {
            String username = userField.getText();
            String password = new String(passField.getPassword());
            if (system.registerUser(username, password)) {
                userField.setText("");
                passField.setText("");
                cardLayout.show(cardPanel, "MainMenu");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "MainMenu"));

        panel.add(userLabel);
        panel.add(userField);
        panel.add(passLabel);
        panel.add(passField);
        panel.add(registerBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "UserRegistration");
    }

    private void createUserLogin() {
        JPanel panel = new JPanel(new GridLayout(3, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel userLabel = new JLabel("Username:");
        JTextField userField = new JTextField();
        JLabel passLabel = new JLabel("Password:");
        JPasswordField passField = new JPasswordField();
        JButton loginBtn = new JButton("Login");
        JButton backBtn = new JButton("Back");

        loginBtn.addActionListener(e -> {
            String username = userField.getText();
            String password = new String(passField.getPassword());
            currentUser = system.loginUser(username, password);
            if (currentUser != null) {
                userField.setText("");
                passField.setText("");
                cardLayout.show(cardPanel, "UserMenu");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "MainMenu"));

        panel.add(userLabel);
        panel.add(userField);
        panel.add(passLabel);
        panel.add(passField);
        panel.add(loginBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "UserLogin");
    }

    private void createAdminLogin() {
        JPanel panel = new JPanel(new GridLayout(3, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel userLabel = new JLabel("Username:");
        JTextField userField = new JTextField();
        JLabel passLabel = new JLabel("Password:");
        JPasswordField passField = new JPasswordField();
        JButton loginBtn = new JButton("Login");
        JButton backBtn = new JButton("Back");

        loginBtn.addActionListener(e -> {
            String username = userField.getText();
            String password = new String(passField.getPassword());
            currentUser = system.loginAdmin(username, password);
            if (currentUser != null) {
                userField.setText("");
                passField.setText("");
                cardLayout.show(cardPanel, "AdminMenu");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "MainMenu"));

        panel.add(userLabel);
        panel.add(userField);
        panel.add(passLabel);
        panel.add(passField);
        panel.add(loginBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "AdminLogin");
    }

    private void createProviderRegistration() {
        JPanel panel = new JPanel(new GridLayout(7, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel userLabel = new JLabel("Username:");
        JTextField userField = new JTextField();
        JLabel passLabel = new JLabel("Password:");
        JPasswordField passField = new JPasswordField();
        JLabel nameLabel = new JLabel("Provider Name:");
        JTextField nameField = new JTextField();
        JLabel numLabel = new JLabel("Ambulance Number:");
        JTextField numField = new JTextField();
        JLabel typeLabel = new JLabel("Service Type:");
        JComboBox<String> typeCombo = new JComboBox<>(new String[] { "Human", "Animal" });
        JButton registerBtn = new JButton("Register");
        JButton backBtn = new JButton("Back");

        registerBtn.addActionListener(e -> {
            String username = userField.getText();
            String password = new String(passField.getPassword());
            String name = nameField.getText();
            String number = numField.getText();
            String type = (String) typeCombo.getSelectedItem();

            if (system.registerAmbulanceProvider(username, password, name, number, type)) {
                userField.setText("");
                passField.setText("");
                nameField.setText("");
                numField.setText("");
                cardLayout.show(cardPanel, "MainMenu");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "MainMenu"));

        panel.add(userLabel);
        panel.add(userField);
        panel.add(passLabel);
        panel.add(passField);
        panel.add(nameLabel);
        panel.add(nameField);
        panel.add(numLabel);
        panel.add(numField);
        panel.add(typeLabel);
        panel.add(typeCombo);
        panel.add(registerBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "ProviderRegistration");
    }

    private void createHospitalRegistration() {
        JPanel panel = new JPanel(new GridLayout(5, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel userLabel = new JLabel("Username:");
        JTextField userField = new JTextField();
        JLabel passLabel = new JLabel("Password:");
        JPasswordField passField = new JPasswordField();
        JLabel nameLabel = new JLabel("Hospital Name:");
        JTextField nameField = new JTextField();
        JLabel locationLabel = new JLabel("Location:");
        JTextField locationField = new JTextField();
        JButton registerBtn = new JButton("Register");
        JButton backBtn = new JButton("Back");

        registerBtn.addActionListener(e -> {
            String username = userField.getText();
            String password = new String(passField.getPassword());
            String name = nameField.getText();
            String location = locationField.getText();

            if (system.registerHospital(username, password, name, location)) {
                userField.setText("");
                passField.setText("");
                nameField.setText("");
                locationField.setText("");
                cardLayout.show(cardPanel, "MainMenu");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "MainMenu"));

        panel.add(userLabel);
        panel.add(userField);
        panel.add(passLabel);
        panel.add(passField);
        panel.add(nameLabel);
        panel.add(nameField);
        panel.add(locationLabel);
        panel.add(locationField);
        panel.add(registerBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "HospitalRegistration");
    }

    private void createHospitalLogin() {
        JPanel panel = new JPanel(new GridLayout(3, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel userLabel = new JLabel("Username:");
        JTextField userField = new JTextField();
        JLabel passLabel = new JLabel("Password:");
        JPasswordField passField = new JPasswordField();
        JButton loginBtn = new JButton("Login");
        JButton backBtn = new JButton("Back");

        loginBtn.addActionListener(e -> {
            String username = userField.getText();
            String password = new String(passField.getPassword());
            currentHospital = system.loginHospital(username, password);
            if (currentHospital != null) {
                userField.setText("");
                passField.setText("");
                cardLayout.show(cardPanel, "HospitalMenu");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "MainMenu"));

        panel.add(userLabel);
        panel.add(userField);
        panel.add(passLabel);
        panel.add(passField);
        panel.add(loginBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "HospitalLogin");
    }

    private void createProviderLogin() {
        JPanel panel = new JPanel(new GridLayout(3, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel userLabel = new JLabel("Username:");
        JTextField userField = new JTextField();
        JLabel passLabel = new JLabel("Password:");
        JPasswordField passField = new JPasswordField();
        JButton loginBtn = new JButton("Login");
        JButton backBtn = new JButton("Back");

        loginBtn.addActionListener(e -> {
            String username = userField.getText();
            String password = new String(passField.getPassword());
            currentProvider = system.loginAmbulanceProvider(username, password);
            if (currentProvider != null) {
                userField.setText("");
                passField.setText("");
                cardLayout.show(cardPanel, "ProviderMenu");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "MainMenu"));

        panel.add(userLabel);
        panel.add(userField);
        panel.add(passLabel);
        panel.add(passField);
        panel.add(loginBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "ProviderLogin");
    }

    private void createUserMenu() {
        JPanel panel = new JPanel(new GridLayout(6, 1, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JButton bookBtn = new JButton("Book Ambulance");
        JButton viewBookingsBtn = new JButton("View My Bookings");
        JButton trackBtn = new JButton("Track Ambulance");
        JButton hospitalsBtn = new JButton("Nearby Hospitals");
        JButton walletBtn = new JButton("Add to Wallet");
        JButton logoutBtn = new JButton("Logout");

        bookBtn.addActionListener(e -> cardLayout.show(cardPanel, "BookingPanel"));
        viewBookingsBtn.addActionListener(e -> showBookings(system.getUserBookings(currentUser.username), "User"));
        trackBtn.addActionListener(e -> trackAmbulance());
        hospitalsBtn.addActionListener(e -> showNearbyHospitals());
        walletBtn.addActionListener(e -> cardLayout.show(cardPanel, "WalletPanel"));
        logoutBtn.addActionListener(e -> {
            currentUser = null;
            cardLayout.show(cardPanel, "MainMenu");
        });

        panel.add(bookBtn);
        panel.add(viewBookingsBtn);
        panel.add(trackBtn);
        panel.add(hospitalsBtn);
        panel.add(walletBtn);
        panel.add(logoutBtn);

        cardPanel.add(panel, "UserMenu");
    }

    private void trackAmbulance() {
        String[] userBookings = system.getUserBookings(currentUser.username);
        if (userBookings.length == 0) {
            JOptionPane.showMessageDialog(null, "No bookings to track!");
            return;
        }

        JComboBox<String> bookingCombo = new JComboBox<>(userBookings);
        JPanel panel = new JPanel(new GridLayout(2, 1, 10, 10));
        panel.add(new JLabel("Select Booking to Track:"));
        panel.add(bookingCombo);

        int result = JOptionPane.showConfirmDialog(null, panel, "Track Ambulance",
                JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            String selected = (String) bookingCombo.getSelectedItem();
            String trackingId = selected.split("\\|")[0].trim().split(":")[1].trim();

            String ambulanceLocation = system.trackAmbulance(trackingId);

            if (!ambulanceLocation.equals("Booking not found or provider not available")) {
                // Ask user for current location
                JTextField userLocationField = new JTextField("Delhi, India");
                JPanel locationPanel = new JPanel(new GridLayout(2, 2, 10, 10));
                locationPanel.add(new JLabel("Your Current Location:"));
                locationPanel.add(userLocationField);

                int locResult = JOptionPane.showConfirmDialog(null, locationPanel, "Enter Your Current Location",
                        JOptionPane.OK_CANCEL_OPTION);
                if (locResult == JOptionPane.OK_OPTION) {
                    String userLocation = userLocationField.getText().trim();
                    if (!userLocation.isEmpty()) {
                        try {
                            // Open Google Maps with directions from user location to ambulance location
                            String encodedUserLocation = URLEncoder.encode(userLocation, "UTF-8");
                            String encodedAmbulanceLocation = URLEncoder.encode(ambulanceLocation, "UTF-8");
                            Desktop.getDesktop().browse(new URI("https://www.google.com/maps/dir/" + encodedUserLocation
                                    + "/" + encodedAmbulanceLocation));
                            JOptionPane.showMessageDialog(null,
                                    "Map opened showing shortest route from your location to ambulance!");
                        } catch (Exception e) {
                            JOptionPane.showMessageDialog(null, "Error opening map: " + e.getMessage()
                                    + "\nAmbulance Location: " + ambulanceLocation);
                        }
                    } else {
                        JOptionPane.showMessageDialog(null, "Please enter your current location!");
                    }
                }
            } else {
                JOptionPane.showMessageDialog(null, "Location: " + ambulanceLocation);
            }
        }
    }

    private void showNearbyHospitals() {
        // Ask user for location
        JTextField locationField = new JTextField("Delhi, India");
        JPanel panel = new JPanel(new GridLayout(2, 1, 10, 10));
        panel.add(new JLabel("Enter Location to Search Hospitals (e.g., Delhi, India):"));
        panel.add(locationField);

        int result = JOptionPane.showConfirmDialog(null, panel, "Search Nearby Hospitals",
                JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            String location = locationField.getText().trim();
            if (location.isEmpty()) {
                JOptionPane.showMessageDialog(null, "Please enter a valid location!");
                return;
            }

            // Geocode the location
            double[] coords = system.geocodeLocation(location);
            double lat = coords[0];
            double lng = coords[1];

            // Get nearest hospital and veterinary
            String nearestHospital = system.getNearestHospital(lat, lng);
            String nearestVet = system.getNearestVeterinary(lat, lng);

            String message = "Nearest Hospital (within 75km of " + location + "):\n" + nearestHospital + "\n\n" +
                    "Nearest Veterinary Hospital:\n" + nearestVet;
            JOptionPane.showMessageDialog(null, message);
        }
    }

    private void createAdminMenu() {
        JPanel panel = new JPanel(new GridLayout(5, 1, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JButton viewUsersBtn = new JButton("View All Users");
        JButton viewProvidersBtn = new JButton("View All Providers");
        JButton viewBookingsBtn = new JButton("View All Bookings");
        JButton saveDataBtn = new JButton("Save Data");
        JButton logoutBtn = new JButton("Logout");

        viewUsersBtn.addActionListener(e -> showUserList());
        viewProvidersBtn.addActionListener(e -> {
            String[] providers = system.getAmbulanceProviders();
            showListDialog(providers, "Ambulance Providers");
        });
        viewBookingsBtn.addActionListener(e -> showBookings(system.getAllBookings(), "Admin"));
        saveDataBtn.addActionListener(e -> system.saveAllData());
        logoutBtn.addActionListener(e -> {
            currentUser = null;
            cardLayout.show(cardPanel, "MainMenu");
        });

        panel.add(viewUsersBtn);
        panel.add(viewProvidersBtn);
        panel.add(viewBookingsBtn);
        panel.add(saveDataBtn);
        panel.add(logoutBtn);

        cardPanel.add(panel, "AdminMenu");
    }

    private void showUserList() {
        Map<String, User> users = system.getUsers();
        if (users.isEmpty()) {
            JOptionPane.showMessageDialog(frame, "No users registered yet.", "User List",
                    JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        String[] columnNames = { "Username", "Wallet Balance" };
        Object[][] data = new Object[users.size()][2];

        int i = 0;
        for (User user : users.values()) {
            data[i][0] = user.username;
            data[i][1] = String.format("$%.2f", user.wallet);
            i++;
        }

        JTable table = new JTable(data, columnNames);
        table.setFillsViewportHeight(true);
        table.setEnabled(false);

        JScrollPane scrollPane = new JScrollPane(table);
        scrollPane.setPreferredSize(new Dimension(400, 300));

        JOptionPane.showMessageDialog(frame, scrollPane, "All Registered Users", JOptionPane.PLAIN_MESSAGE);
    }

    private void showListDialog(String[] items, String title) {
        JTextArea textArea = new JTextArea(10, 30);
        textArea.setEditable(false);

        for (String item : items) {
            textArea.append(item + "\n");
        }

        JScrollPane scrollPane = new JScrollPane(textArea);
        JOptionPane.showMessageDialog(frame, scrollPane, title, JOptionPane.PLAIN_MESSAGE);
    }

    private void createProviderMenu() {
        JPanel panel = new JPanel(new GridLayout(6, 1, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JButton viewBookingsBtn = new JButton("View My Bookings");
        JButton manageBookingsBtn = new JButton("Manage Bookings");
        JButton completeRideBtn = new JButton("Complete Ride");
        JButton updateLocationBtn = new JButton("Update Location");
        JButton trackUserBtn = new JButton("Track User");
        JButton viewWalletBtn = new JButton("View Wallet");
        JButton logoutBtn = new JButton("Logout");

        viewBookingsBtn.addActionListener(e -> {
            String[] bookings = system.getProviderBookings(currentProvider.name);
            showBookings(bookings, "Provider");
        });

        manageBookingsBtn.addActionListener(e -> manageBookings());
        completeRideBtn.addActionListener(e -> completeRide());
        updateLocationBtn.addActionListener(e -> updateProviderLocation());
        trackUserBtn.addActionListener(e -> trackUser());
        viewWalletBtn.addActionListener(e -> {
            JOptionPane.showMessageDialog(null, "Current Wallet Balance: $" + currentProvider.wallet,
                    "Wallet", JOptionPane.INFORMATION_MESSAGE);
        });

        logoutBtn.addActionListener(e -> {
            currentProvider = null;
            cardLayout.show(cardPanel, "MainMenu");
        });

        panel.add(viewBookingsBtn);
        panel.add(manageBookingsBtn);
        panel.add(completeRideBtn);
        panel.add(updateLocationBtn);
        panel.add(trackUserBtn);
        panel.add(viewWalletBtn);
        panel.add(logoutBtn);

        cardPanel.add(panel, "ProviderMenu");
    }

    private void createHospitalMenu() {
        JPanel panel = new JPanel(new GridLayout(6, 1, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JButton nearbyHospitalsBtn = new JButton("Nearby Hospitals");
        JButton addDoctorBtn = new JButton("Add Doctor");
        JButton arrangeDoctorBtn = new JButton("Arrange Doctor");
        JButton viewPatientsBtn = new JButton("View Patients");
        JButton viewPatientLocationBtn = new JButton("View Patient Location");
        JButton logoutBtn = new JButton("Logout");

        nearbyHospitalsBtn.addActionListener(e -> showNearbyHospitalsForHospital());
        addDoctorBtn.addActionListener(e -> cardLayout.show(cardPanel, "AddDoctorPanel"));
        arrangeDoctorBtn.addActionListener(e -> {
            // Populate the combo box before showing the panel
            arrangeDoctorBookingCombo.removeAllItems();
            String[] bookings = system.getHospitalBookings(currentHospital.name);
            for (String booking : bookings) {
                arrangeDoctorBookingCombo.addItem(booking);
            }
            cardLayout.show(cardPanel, "ArrangeDoctorPanel");
        });
        viewPatientsBtn.addActionListener(e -> showHospitalPatients());
        viewPatientLocationBtn.addActionListener(e -> viewPatientLocation());
        logoutBtn.addActionListener(e -> {
            currentHospital = null;
            cardLayout.show(cardPanel, "MainMenu");
        });

        panel.add(nearbyHospitalsBtn);
        panel.add(addDoctorBtn);
        panel.add(arrangeDoctorBtn);
        panel.add(viewPatientsBtn);
        panel.add(viewPatientLocationBtn);
        panel.add(logoutBtn);

        cardPanel.add(panel, "HospitalMenu");
    }

    private void updateProviderLocation() {
        JTextField locationField = new JTextField(currentProvider.currentLocation);

        JPanel panel = new JPanel(new GridLayout(2, 2, 10, 10));
        panel.add(new JLabel("Current Location:"));
        panel.add(locationField);

        int result = JOptionPane.showConfirmDialog(null, panel, "Update Location",
                JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            String location = locationField.getText().trim();
            if (!location.isEmpty()) {
                currentProvider.updateLocation(location);
                JOptionPane.showMessageDialog(null, "Location updated successfully!");
            } else {
                JOptionPane.showMessageDialog(null, "Please enter a valid location!");
            }
        }
    }

    private void createBookingPanel() {
        JPanel panel = new JPanel(new GridLayout(6, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel typeLabel = new JLabel("Service Type:");
        JComboBox<String> typeCombo = new JComboBox<>(new String[] { "Human", "Animal" });
        JLabel nameLabel = new JLabel("Your Name:");
        JTextField nameField = new JTextField();
        JLabel mobileLabel = new JLabel("Mobile Number:");
        JTextField mobileField = new JTextField();
        JLabel pickupLocationLabel = new JLabel("Pickup Location:");
        JTextField pickupLocationField = new JTextField();
        JLabel providerLabel = new JLabel("Select Provider:");
        JComboBox<String> providerCombo = new JComboBox<>();

        typeCombo.addActionListener(e -> {
            String selectedType = (String) typeCombo.getSelectedItem();
            updateProviderCombo(providerCombo, selectedType);
        });

        updateProviderCombo(providerCombo, (String) typeCombo.getSelectedItem());

        JButton bookBtn = new JButton("Book Now");
        JButton backBtn = new JButton("Back");

        bookBtn.addActionListener(e -> {
            String type = (String) typeCombo.getSelectedItem();
            String name = nameField.getText();
            String mobile = mobileField.getText();
            String provider = (String) providerCombo.getSelectedItem();
            String pickupLocation = pickupLocationField.getText().trim();

            if (provider == null || provider.isEmpty() || provider.startsWith("No providers")) {
                JOptionPane.showMessageDialog(null, "Please select a valid provider!");
                return;
            }
            if (pickupLocation.isEmpty()) {
                JOptionPane.showMessageDialog(null, "Please enter a pickup location!");
                return;
            }

            String trackingId = system.bookAmbulance(currentUser, type, name, mobile, provider, pickupLocation);
            if (trackingId != null) {
                JOptionPane.showMessageDialog(null, "Booking successful! Tracking ID: " + trackingId);
                nameField.setText("");
                mobileField.setText("");
                pickupLocationField.setText("");
                cardLayout.show(cardPanel, "UserMenu");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "UserMenu"));

        panel.add(typeLabel);
        panel.add(typeCombo);
        panel.add(nameLabel);
        panel.add(nameField);
        panel.add(mobileLabel);
        panel.add(mobileField);
        panel.add(pickupLocationLabel);
        panel.add(pickupLocationField);
        panel.add(providerLabel);
        panel.add(providerCombo);
        panel.add(bookBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "BookingPanel");
    }

    private void updateProviderCombo(JComboBox<String> providerCombo, String serviceType) {
        providerCombo.removeAllItems();
        String[] providers = system.getAmbulanceProvidersByType(serviceType);

        if (providers.length == 0) {
            providerCombo.addItem("No providers available for " + serviceType + " services");
        } else {
            for (String provider : providers) {
                providerCombo.addItem(provider);
            }
        }
    }

    private void createWalletPanel() {
        JPanel panel = new JPanel(new GridLayout(3, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel amountLabel = new JLabel("Amount to Add:");
        JTextField amountField = new JTextField();
        JButton addBtn = new JButton("Add Funds");
        JButton backBtn = new JButton("Back");

        addBtn.addActionListener(e -> {
            try {
                double amount = Double.parseDouble(amountField.getText());
                system.addToWallet(currentUser, amount);
                JOptionPane.showMessageDialog(null, "$" + amount + " added to your wallet!");
                amountField.setText("");
                cardLayout.show(cardPanel, "UserMenu");
            } catch (NumberFormatException ex) {
                JOptionPane.showMessageDialog(null, "Please enter a valid amount!");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "UserMenu"));

        panel.add(amountLabel);
        panel.add(amountField);
        panel.add(addBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "WalletPanel");
    }

    private void createAddDoctorPanel() {
        JPanel panel = new JPanel(new GridLayout(3, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel doctorNameLabel = new JLabel("Doctor Name:");
        JTextField doctorNameField = new JTextField();
        JButton addBtn = new JButton("Add Doctor");
        JButton backBtn = new JButton("Back");

        addBtn.addActionListener(e -> {
            String doctorName = doctorNameField.getText().trim();
            if (!doctorName.isEmpty()) {
                if (system.addDoctor(doctorName, currentHospital.name)) {
                    doctorNameField.setText("");
                    cardLayout.show(cardPanel, "HospitalMenu");
                }
            } else {
                JOptionPane.showMessageDialog(null, "Please enter a doctor name!");
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "HospitalMenu"));

        panel.add(doctorNameLabel);
        panel.add(doctorNameField);
        panel.add(addBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "AddDoctorPanel");
    }

    private void createArrangeDoctorPanel() {
        JPanel panel = new JPanel(new GridLayout(3, 2, 10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel bookingLabel = new JLabel("Select Patient Booking:");
        arrangeDoctorBookingCombo = new JComboBox<>();
        JButton assignBtn = new JButton("Assign Doctor");
        JButton backBtn = new JButton("Back");

        // Populate bookings that need doctors - will be done when panel is shown
        if (currentHospital != null) {
            String[] bookings = system.getHospitalBookings(currentHospital.name);
            for (String booking : bookings) {
                if (booking.contains("Not Assigned")) {
                    arrangeDoctorBookingCombo.addItem(booking);
                }
            }
        }

        assignBtn.addActionListener(e -> {
            String selected = (String) arrangeDoctorBookingCombo.getSelectedItem();
            if (selected != null) {
                String trackingId = selected.split("\\|")[0].trim().split(":")[1].trim();
                String[] availableDoctors = system.getAvailableDoctorsByHospital(currentHospital.name);
                if (availableDoctors.length > 0) {
                    String doctorName = (String) JOptionPane.showInputDialog(null, "Select Doctor:", "Assign Doctor",
                            JOptionPane.QUESTION_MESSAGE, null, availableDoctors, availableDoctors[0]);
                    if (doctorName != null) {
                        system.assignDoctorToBooking(trackingId, doctorName);
                        cardLayout.show(cardPanel, "HospitalMenu");
                    }
                } else {
                    JOptionPane.showMessageDialog(null, "No available doctors!");
                }
            }
        });

        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "HospitalMenu"));

        panel.add(bookingLabel);
        panel.add(arrangeDoctorBookingCombo);
        panel.add(assignBtn);
        panel.add(backBtn);

        cardPanel.add(panel, "ArrangeDoctorPanel");
    }

    private void showNearbyHospitalsForHospital() {
        JTextField locationField = new JTextField(currentHospital.location);
        JPanel panel = new JPanel(new GridLayout(2, 1, 10, 10));
        panel.add(new JLabel("Enter Location to Search Hospitals (e.g., Delhi, India):"));
        panel.add(locationField);

        int result = JOptionPane.showConfirmDialog(null, panel, "Search Nearby Hospitals",
                JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            String location = locationField.getText().trim();
            if (location.isEmpty()) {
                JOptionPane.showMessageDialog(null, "Please enter a valid location!");
                return;
            }

            double[] coords = system.geocodeLocation(location);
            double lat = coords[0];
            double lng = coords[1];

            String nearestHospital = system.getNearestHospital(lat, lng);
            String nearestVet = system.getNearestVeterinary(lat, lng);

            String message = "Nearest Hospital (within 75km of " + location + "):\n" + nearestHospital + "\n\n" +
                    "Nearest Veterinary Hospital:\n" + nearestVet;
            JOptionPane.showMessageDialog(null, message);
        }
    }

    private void showHospitalPatients() {
        String[] patients = system.getHospitalBookings(currentHospital.name);
        showBookings(patients, "Hospital Patients");
    }

    private void viewPatientLocation() {
        String[] patients = system.getHospitalBookings(currentHospital.name);
        if (patients.length == 0) {
            JOptionPane.showMessageDialog(null, "No patients to view!");
            return;
        }

        JComboBox<String> patientCombo = new JComboBox<>(patients);
        JPanel panel = new JPanel(new GridLayout(2, 1, 10, 10));
        panel.add(new JLabel("Select Patient to View Location:"));
        panel.add(patientCombo);

        int result = JOptionPane.showConfirmDialog(null, panel, "View Patient Location",
                JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            String selected = (String) patientCombo.getSelectedItem();
            if (selected != null) {
                String location = selected.split("Location: ")[1].split(" \\|")[0];
                try {
                    String encodedLocation = URLEncoder.encode(location, "UTF-8");
                    Desktop.getDesktop().browse(new URI("https://www.google.com/maps/search/" + encodedLocation));
                    JOptionPane.showMessageDialog(null, "Map opened showing patient's location!");
                } catch (Exception e) {
                    JOptionPane.showMessageDialog(null,
                            "Error opening map: " + e.getMessage() + "\nLocation: " + location);
                }
            }
        }
    }

    private void showBookings(String[] bookings, String userType) {
        JFrame bookingsFrame = new JFrame(userType + " Bookings");
        bookingsFrame.setSize(600, 400);
        bookingsFrame.setLocationRelativeTo(frame);
        bookingsFrame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);

        JTextArea textArea = new JTextArea();
        textArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(textArea);

        for (String booking : bookings) {
            textArea.append(booking + "\n");
        }

        bookingsFrame.add(scrollPane);
        bookingsFrame.setVisible(true);
    }

    private void manageBookings() {
        String[] providerBookings = system.getProviderBookings(currentProvider.name);
        if (providerBookings.length == 0) {
            JOptionPane.showMessageDialog(null, "No bookings to manage!");
            return;
        }

        JComboBox<String> bookingCombo = new JComboBox<>(providerBookings);
        JComboBox<String> actionCombo = new JComboBox<>(new String[] { "Accept", "Reject" });

        JPanel panel = new JPanel(new GridLayout(3, 2, 10, 10));
        panel.add(new JLabel("Select Booking:"));
        panel.add(bookingCombo);
        panel.add(new JLabel("Action:"));
        panel.add(actionCombo);

        int result = JOptionPane.showConfirmDialog(null, panel, "Manage Bookings",
                JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            String selected = (String) bookingCombo.getSelectedItem();
            String trackingId = selected.split("\\|")[0].trim().split(":")[1].trim();
            boolean accept = actionCombo.getSelectedItem().equals("Accept");

            currentProvider.manageBooking(system, trackingId, accept);
            JOptionPane.showMessageDialog(null, "Booking " + (accept ? "accepted" : "rejected") + "!");
        }
    }

    private void completeRide() {
        String[] providerBookings = system.getProviderBookings(currentProvider.name);
        if (providerBookings.length == 0) {
            JOptionPane.showMessageDialog(null, "No bookings to complete!");
            return;
        }

        JComboBox<String> bookingCombo = new JComboBox<>(providerBookings);
        JPanel panel = new JPanel(new GridLayout(2, 1, 10, 10));
        panel.add(new JLabel("Select Booking to Complete:"));
        panel.add(bookingCombo);

        int result = JOptionPane.showConfirmDialog(null, panel, "Complete Ride",
                JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            String selected = (String) bookingCombo.getSelectedItem();
            String trackingId = selected.split("\\|")[0].trim().split(":")[1].trim();

            if (system.completeRide(currentProvider, trackingId)) {
                JOptionPane.showMessageDialog(null, "Ride completed! Payment added to your wallet.");
            } else {
                JOptionPane.showMessageDialog(null, "Could not complete ride. Booking may not be accepted.");
            }
        }
    }

    private void trackUser() {
        String[] providerBookings = system.getProviderBookings(currentProvider.name);
        if (providerBookings.length == 0) {
            JOptionPane.showMessageDialog(null, "No bookings to track!");
            return;
        }

        JComboBox<String> bookingCombo = new JComboBox<>(providerBookings);
        JPanel panel = new JPanel(new GridLayout(2, 1, 10, 10));
        panel.add(new JLabel("Select Booking to Track User:"));
        panel.add(bookingCombo);

        int result = JOptionPane.showConfirmDialog(null, panel, "Track User",
                JOptionPane.OK_CANCEL_OPTION);
        if (result == JOptionPane.OK_OPTION) {
            String selected = (String) bookingCombo.getSelectedItem();
            String trackingId = selected.split("\\|")[0].trim().split(":")[1].trim();

            // Find the booking to get pickup location
            String pickupLocation = null;
            for (Booking booking : system.getBookings()) {
                if (booking.trackingId.equals(trackingId)
                        && booking.ambulanceProviderName.equals(currentProvider.name)) {
                    pickupLocation = booking.pickupLocation;
                    break;
                }
            }

            if (pickupLocation != null) {
                try {
                    // Open Google Maps with directions from provider's current location to user's
                    // pickup location
                    String encodedProviderLocation = URLEncoder.encode(currentProvider.currentLocation, "UTF-8");
                    String encodedPickupLocation = URLEncoder.encode(pickupLocation, "UTF-8");
                    Desktop.getDesktop().browse(new URI("https://www.google.com/maps/dir/" + encodedProviderLocation
                            + "/" + encodedPickupLocation));
                    JOptionPane.showMessageDialog(null,
                            "Map opened showing shortest route from your location to user's pickup location!");
                } catch (Exception e) {
                    JOptionPane.showMessageDialog(null,
                            "Error opening map: " + e.getMessage() + "\nPickup Location: " + pickupLocation);
                }
            } else {
                JOptionPane.showMessageDialog(null, "Booking not found!");
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new AmbulanceBookingGUI());
    }
}