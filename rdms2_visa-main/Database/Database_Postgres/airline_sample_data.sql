-- Sample Data for Airline Management System
-- Insert example records to demonstrate the database structure

-- Insert Aircraft with specific UUIDs for reference
INSERT INTO aircraft (aircraft_id, code_number, brand, model, passenger_capacity, range_km, is_active, status) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'TC-JRO', 'Boeing', '737-800', 189, 5436, true, 'active'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'TC-JRN', 'Airbus', 'A320-200', 174, 6150, true, 'active'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'TC-JRM', 'Boeing', '777-300ER', 349, 13649, true, 'active'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'TC-JRK', 'Airbus', 'A321neo', 220, 7400, false, 'maintenance'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 'TC-JRL', 'Boeing', '787-9', 290, 14010, false, 'repair'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a16', 'TC-JRJ', 'Airbus', 'A330-300', 300, 11750, true, 'active');

-- Insert Passengers with specific UUIDs for reference
INSERT INTO passengers (passenger_id, passenger_number, first_name, last_name, birth_date, gender) VALUES
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'PAX001', 'Burak', 'Yılmaz', '1985-03-15', 'M'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'PAX002', 'Ali', 'Demir', '1990-07-22', 'M'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'PAX003', 'Murat', 'Kaya', '1988-11-10', 'M'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', 'PAX004', 'Faik', 'Şakrak', '1992-05-18', 'M'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', 'PAX005', 'Ali', 'Özkan', '1987-09-25', 'M'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', 'PAX006', 'Zeynep', 'Arslan', '1995-12-08', 'F'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27', 'PAX007', 'Mustafa', 'Çelik', '1983-02-14', 'M'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28', 'PAX008', 'Elif', 'Aydın', '1998-06-30', 'F');

-- Insert Passenger Phone Numbers
-- Each passenger can have home, mobile, and work phone numbers
INSERT INTO passenger_phones (passenger_id, phone_type, phone_number, is_primary) VALUES
-- PAX001 - Ahmet Yılmaz
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'mobile', '05321234567', true),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'home', '03123456789', false),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'work', '03129876543', false),
-- PAX002 - Ayşe Demir
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'mobile', '05331234567', true),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'home', '02164567890', false),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'work', '02169876543', false),
-- PAX003 - Mehmet Kaya
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'mobile', '05341234567', true),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'home', '02325678901', false),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'work', '02329876543', false),
-- PAX004 - Fatma Şahin
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', 'mobile', '05351234567', true),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', 'home', '03126789012', false),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', 'work', '03129876544', false),
-- PAX005 - Ali Özkan
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', 'mobile', '05361234567', true),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', 'home', '02167890123', false),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', 'work', '02169876545', false),
-- PAX006 - Zeynep Arslan
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', 'mobile', '05371234567', true),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', 'home', '02328901234', false),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', 'work', '02329876546', false),
-- PAX007 - Mustafa Çelik
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27', 'mobile', '05381234567', true),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27', 'home', '03129012345', false),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27', 'work', '03129876547', false),
-- PAX008 - Elif Aydın
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28', 'mobile', '05391234567', true),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28', 'home', '02160123456', false),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28', 'work', '02169876548', false);

-- Insert Passenger Addresses
-- Each passenger can have multiple addresses (home, work, billing, other)
INSERT INTO passenger_addresses (passenger_id, address_type, address_line, city, country, is_primary) VALUES
-- PAX001 - Ahmet Yılmaz
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'home', 'Kızılay Mah. Atatürk Bulvarı No:45 Çankaya', 'Ankara', 'Türkiye', true),
-- PAX002 - Ayşe Demir
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'home', 'Kadıköy Mah. Bağdat Cad. No:123 Kadıköy', 'İstanbul', 'Türkiye', true),
-- PAX003 - Mehmet Kaya
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'home', 'Alsancak Mah. Cumhuriyet Bulvarı No:78 Konak', 'İzmir', 'Türkiye', true),
-- PAX004 - Fatma Şahin
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', 'home', 'Bahçelievler Mah. Eskişehir Yolu No:234 Yenimahalle', 'Ankara', 'Türkiye', true),
-- PAX005 - Ali Özkan
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', 'home', 'Beşiktaş Mah. Barbaros Bulvarı No:56 Beşiktaş', 'İstanbul', 'Türkiye', true),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', 'work', 'Levent Mah. Büyükdere Cad. No:100 Şişli', 'İstanbul', 'Türkiye', false),
-- PAX006 - Zeynep Arslan
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', 'home', 'Karşıyaka Mah. Atatürk Cad. No:89 Karşıyaka', 'İzmir', 'Türkiye', true),
-- PAX007 - Mustafa Çelik
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27', 'home', 'Ümitköy Mah. Konya Yolu No:67 Çankaya', 'Ankara', 'Türkiye', true),
-- PAX008 - Elif Aydın
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28', 'home', 'Üsküdar Mah. İstanbul Cad. No:34 Üsküdar', 'İstanbul', 'Türkiye', true);

-- Insert Airports (using real UUIDs from current database)
-- These match the airports already created in the database
INSERT INTO airports (airport_id, airport_name, iata_code, icao_code, city, country, is_active) VALUES
('de14e3c0-8159-4087-8c97-8554e26fa3ff', 'Istanbul Airport', 'IST', 'LTFM', 'Istanbul', 'Turkey', true),
('64aeba64-a98f-4f02-bd77-e9141846974e', 'Sabiha Gokcen International Airport', 'SAW', 'LTFJ', 'Istanbul', 'Turkey', true),
('05c09203-a50c-4715-8f61-3c87699b9eef', 'Ankara Esenboga Airport', 'ESB', 'LTAC', 'Ankara', 'Turkey', true),
('186dd471-47a6-4b89-a7b6-d7dbecc66277', 'Izmir Adnan Menderes Airport', 'ADB', 'LTBJ', 'Izmir', 'Turkey', true),
('3a3a860a-7052-4983-bb4c-1eb4a28278c1', 'Antalya Airport', 'AYT', 'LTAI', 'Antalya', 'Turkey', true),
('10e6a9a2-f4fe-48da-80fa-ecc2773d21ca', 'John F. Kennedy International Airport', 'JFK', 'KJFK', 'New York', 'United States', true),
('49e069d5-39e4-4843-9214-26cbdd815733', 'London Heathrow Airport', 'LHR', 'EGLL', 'London', 'United Kingdom', true),
('04436ff2-72d4-4f63-ae63-8e50ea652813', 'Charles de Gaulle Airport', 'CDG', 'LFPG', 'Paris', 'France', true),
('1d0f7d3d-87fc-491d-aa24-cbafc3076710', 'Dubai International Airport', 'DXB', 'OMDB', 'Dubai', 'United Arab Emirates', true),
('9614865d-8d3c-454f-a266-eca15df29f0b', 'Frankfurt Airport', 'FRA', 'EDDF', 'Frankfurt', 'Germany', true)
ON CONFLICT (iata_code) DO NOTHING;

-- Insert Flights with airport foreign keys (new structure)
INSERT INTO flights (flight_id, flight_number, departure_airport_id, arrival_airport_id, flight_date, flight_time, aircraft_id, status) VALUES
-- IST to ESB
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'TK101', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '05c09203-a50c-4715-8f61-3c87699b9eef', '2026-02-20', '08:00:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'scheduled'),
-- ESB to IST
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'TK102', '05c09203-a50c-4715-8f61-3c87699b9eef', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '2026-02-20', '10:30:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'scheduled'),
-- IST to ADB
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'TK201', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '186dd471-47a6-4b89-a7b6-d7dbecc66277', '2026-02-21', '09:15:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'scheduled'),
-- ADB to IST
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'TK202', '186dd471-47a6-4b89-a7b6-d7dbecc66277', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '2026-02-21', '12:00:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'scheduled'),
-- IST to LHR
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a35', 'TK301', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '49e069d5-39e4-4843-9214-26cbdd815733', '2026-02-22', '14:00:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'scheduled'),
-- LHR to IST
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a36', 'TK302', '49e069d5-39e4-4843-9214-26cbdd815733', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '2026-02-23', '18:30:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'scheduled'),
-- ESB to ADB
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a37', 'TK401', '05c09203-a50c-4715-8f61-3c87699b9eef', '186dd471-47a6-4b89-a7b6-d7dbecc66277', '2026-02-24', '11:00:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a16', 'scheduled'),
-- IST to AYT
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a38', 'TK501', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '3a3a860a-7052-4983-bb4c-1eb4a28278c1', '2026-02-25', '07:30:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'scheduled'),
-- Additional international flights
-- IST to JFK
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a39', 'TK003', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '10e6a9a2-f4fe-48da-80fa-ecc2773d21ca', '2026-02-26', '23:30:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'scheduled'),
-- IST to CDG
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a40', 'TK1827', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '04436ff2-72d4-4f63-ae63-8e50ea652813', '2026-02-27', '10:15:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'scheduled'),
-- IST to DXB
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'TK763', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '1d0f7d3d-87fc-491d-aa24-cbafc3076710', '2026-02-28', '02:45:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a16', 'scheduled'),
-- IST to FRA
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'TK1589', 'de14e3c0-8159-4087-8c97-8554e26fa3ff', '9614865d-8d3c-454f-a266-eca15df29f0b', '2026-03-01', '07:45:00', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'scheduled');

-- Insert Flight Bookings with UUID references
-- Flight TK101: Istanbul to Ankara (3 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', '12A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '12B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', '15C', 'confirmed');

-- Flight TK102: Ankara to Istanbul (2 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', '8D', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', '8E', 'confirmed');

-- Flight TK201: Istanbul to Izmir (4 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '5A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', '5B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', '10C', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', '10D', 'confirmed');

-- Flight TK202: Izmir to Istanbul (3 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', '7A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', '7B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27', '9C', 'confirmed');

-- Flight TK301: Istanbul to London (5 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a35', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', '20A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a35', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', '20B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a35', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', '21A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a35', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27', '21B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a35', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28', '22A', 'confirmed');

-- Flight TK302: London to Istanbul (2 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a36', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', '18C', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a36', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', '18D', 'confirmed');

-- Flight TK401: Ankara to Izmir (1 passenger - minimum requirement)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a37', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '3A', 'confirmed');

-- Flight TK501: Istanbul to Antalya (4 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a38', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '6A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a38', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', '6B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a38', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', '7A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a38', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28', '7B', 'confirmed');

-- Flight TK003: Istanbul to New York (6 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a39', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', '30A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a39', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '30B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a39', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', '31A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a39', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', '31B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a39', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27', '32A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a39', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28', '32B', 'confirmed');

-- Flight TK1827: Istanbul to Paris (3 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a40', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', '14A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a40', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', '14B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a40', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', '15A', 'confirmed');

-- Flight TK763: Istanbul to Dubai (5 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', '25A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', '25B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', '26A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', '26B', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28', '27A', 'confirmed');

-- Flight TK1589: Istanbul to Frankfurt (2 passengers)
INSERT INTO flight_bookings (flight_id, passenger_id, seat_number, booking_status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26', '11A', 'confirmed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27', '11B', 'confirmed');

-- Verification Queries
SELECT '=== AIRCRAFT SUMMARY ===' AS info;
SELECT 
    a.aircraft_id,
    a.code_number, 
    a.brand, 
    a.model, 
    a.status, 
    COUNT(f.flight_id) as total_flights
FROM aircraft a
LEFT JOIN flights f ON a.aircraft_id = f.aircraft_id
GROUP BY a.aircraft_id, a.code_number, a.brand, a.model, a.status
ORDER BY a.code_number;

SELECT '=== PASSENGER SUMMARY ===' AS info;
SELECT 
    p.passenger_id,
    p.passenger_number,
    p.first_name,
    p.last_name,
    COUNT(fb.booking_id) as total_flights
FROM passengers p
LEFT JOIN flight_bookings fb ON p.passenger_id = fb.passenger_id
GROUP BY p.passenger_id, p.passenger_number, p.first_name, p.last_name
ORDER BY total_flights DESC;

SELECT '=== FLIGHT SUMMARY ===' AS info;
SELECT 
    f.flight_id,
    f.flight_number,
    dep.iata_code || ' - ' || dep.city as departure,
    arr.iata_code || ' - ' || arr.city as arrival,
    f.flight_date,
    f.flight_time,
    a.code_number as aircraft,
    COUNT(fb.booking_id) as passenger_count
FROM flights f
JOIN airports dep ON f.departure_airport_id = dep.airport_id
JOIN airports arr ON f.arrival_airport_id = arr.airport_id
JOIN aircraft a ON f.aircraft_id = a.aircraft_id
LEFT JOIN flight_bookings fb ON f.flight_id = fb.flight_id
GROUP BY f.flight_id, f.flight_number, dep.iata_code, dep.city, arr.iata_code, arr.city, f.flight_date, f.flight_time, a.code_number
ORDER BY f.flight_date, f.flight_time;

SELECT '=== AIRPORT SUMMARY ===' AS info;
SELECT 
    a.iata_code,
    a.icao_code,
    a.airport_name,
    a.city,
    a.country,
    COUNT(DISTINCT d.flight_id) as departures,
    COUNT(DISTINCT arr.flight_id) as arrivals
FROM airports a
LEFT JOIN flights d ON a.airport_id = d.departure_airport_id
LEFT JOIN flights arr ON a.airport_id = arr.arrival_airport_id
GROUP BY a.airport_id, a.iata_code, a.icao_code, a.airport_name, a.city, a.country
ORDER BY a.iata_code;
