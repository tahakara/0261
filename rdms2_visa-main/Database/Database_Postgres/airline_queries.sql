-- Useful Queries for Airline Management System
-- Common queries and reports

-- ============================================
-- 1. LIST ALL ACTIVE AIRCRAFT
-- ============================================
SELECT 
    code_number,
    brand,
    model,
    passenger_capacity,
    range_km,
    status
FROM aircraft
WHERE is_active = true
ORDER BY brand, model;

-- ============================================
-- 2. FIND ALL FLIGHTS FOR A SPECIFIC AIRCRAFT
-- ============================================
SELECT 
    f.flight_number,
    f.departure_point,
    f.arrival_point,
    f.flight_date,
    f.flight_time,
    f.status
FROM flights f
JOIN aircraft a ON f.aircraft_id = a.aircraft_id
WHERE a.code_number = 'TC-JRO'
ORDER BY f.flight_date, f.flight_time;

-- ============================================
-- 3. GET ALL FLIGHTS FOR A SPECIFIC PASSENGER
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name,
    p.last_name,
    f.flight_number,
    f.departure_point,
    f.arrival_point,
    f.flight_date,
    f.flight_time,
    fb.seat_number,
    fb.booking_status
FROM passengers p
JOIN flight_bookings fb ON p.passenger_id = fb.passenger_id
JOIN flights f ON fb.flight_id = f.flight_id
WHERE p.passenger_number = 'PAX001'
ORDER BY f.flight_date, f.flight_time;

-- ============================================
-- 4. GET PASSENGER LIST FOR A SPECIFIC FLIGHT
-- ============================================
SELECT 
    f.flight_number,
    f.departure_point,
    f.arrival_point,
    f.flight_date,
    p.passenger_number,
    p.first_name,
    p.last_name,
    fb.seat_number,
    fb.booking_status
FROM flights f
JOIN flight_bookings fb ON f.flight_id = fb.flight_id
JOIN passengers p ON fb.passenger_id = p.passenger_id
WHERE f.flight_number = 'TK101'
ORDER BY fb.seat_number;

-- ============================================
-- 5. AIRCRAFT UTILIZATION REPORT
-- Shows how many flights each aircraft has
-- ============================================
SELECT 
    a.code_number,
    a.brand,
    a.model,
    a.status,
    COUNT(f.flight_id) as total_flights,
    MIN(f.flight_date) as first_flight,
    MAX(f.flight_date) as last_flight
FROM aircraft a
LEFT JOIN flights f ON a.aircraft_id = f.aircraft_id
GROUP BY a.aircraft_id, a.code_number, a.brand, a.model, a.status
ORDER BY total_flights DESC;

-- ============================================
-- 6. FLIGHTS WITH AVAILABLE CAPACITY
-- Shows flights that are not fully booked
-- ============================================
SELECT 
    f.flight_number,
    f.departure_point,
    f.arrival_point,
    f.flight_date,
    a.passenger_capacity,
    COUNT(fb.booking_id) as booked_seats,
    a.passenger_capacity - COUNT(fb.booking_id) as available_seats
FROM flights f
JOIN aircraft a ON f.aircraft_id = a.aircraft_id
LEFT JOIN flight_bookings fb ON f.flight_id = fb.flight_id
GROUP BY f.flight_id, f.flight_number, f.departure_point, f.arrival_point, f.flight_date, a.passenger_capacity
HAVING COUNT(fb.booking_id) < a.passenger_capacity
ORDER BY f.flight_date;

-- ============================================
-- 7. PASSENGER FLIGHT HISTORY SUMMARY
-- Shows total flights per passenger
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name,
    p.last_name,
    COUNT(fb.booking_id) as total_flights,
    MIN(f.flight_date) as first_flight_date,
    MAX(f.flight_date) as last_flight_date
FROM passengers p
LEFT JOIN flight_bookings fb ON p.passenger_id = fb.passenger_id
LEFT JOIN flights f ON fb.flight_id = f.flight_id
GROUP BY p.passenger_id, p.passenger_number, p.first_name, p.last_name
HAVING COUNT(fb.booking_id) >= 1  -- Passengers with at least one flight
ORDER BY total_flights DESC;

-- ============================================
-- 8. DAILY FLIGHT SCHEDULE
-- Shows all flights for a specific date
-- ============================================
SELECT 
    f.flight_number,
    f.departure_point,
    f.arrival_point,
    f.flight_time,
    a.code_number as aircraft,
    a.brand || ' ' || a.model as aircraft_type,
    COUNT(fb.booking_id) as passenger_count,
    a.passenger_capacity,
    f.status
FROM flights f
JOIN aircraft a ON f.aircraft_id = a.aircraft_id
LEFT JOIN flight_bookings fb ON f.flight_id = fb.flight_id
WHERE f.flight_date = '2026-02-20'
GROUP BY f.flight_id, f.flight_number, f.departure_point, f.arrival_point, 
         f.flight_time, a.code_number, a.brand, a.model, a.passenger_capacity, f.status
ORDER BY f.flight_time;

-- ============================================
-- 9. AIRCRAFT MAINTENANCE STATUS
-- Shows all aircraft in maintenance or repair
-- ============================================
SELECT 
    code_number,
    brand,
    model,
    status,
    passenger_capacity,
    updated_at as status_updated
FROM aircraft
WHERE status IN ('maintenance', 'repair')
ORDER BY updated_at DESC;

-- ============================================
-- 10. ROUTE POPULARITY
-- Shows most popular routes
-- ============================================
SELECT 
    f.departure_point,
    f.arrival_point,
    COUNT(DISTINCT f.flight_id) as total_flights,
    COUNT(fb.booking_id) as total_passengers,
    ROUND(AVG(COUNT(fb.booking_id)) OVER (PARTITION BY f.departure_point, f.arrival_point), 2) as avg_passengers_per_flight
FROM flights f
LEFT JOIN flight_bookings fb ON f.flight_id = fb.flight_id
GROUP BY f.departure_point, f.arrival_point
ORDER BY total_passengers DESC;

-- ============================================
-- 11. FIND PASSENGERS WHO FLEW TOGETHER
-- Shows passengers who were on the same flight
-- ============================================
SELECT DISTINCT
    f.flight_number,
    f.flight_date,
    f.departure_point,
    f.arrival_point,
    p1.passenger_number as passenger_1,
    p1.first_name || ' ' || p1.last_name as name_1,
    p2.passenger_number as passenger_2,
    p2.first_name || ' ' || p2.last_name as name_2
FROM flight_bookings fb1
JOIN flight_bookings fb2 ON fb1.flight_id = fb2.flight_id AND fb1.passenger_id < fb2.passenger_id
JOIN passengers p1 ON fb1.passenger_id = p1.passenger_id
JOIN passengers p2 ON fb2.passenger_id = p2.passenger_id
JOIN flights f ON fb1.flight_id = f.flight_id
ORDER BY f.flight_date, f.flight_number;

-- ============================================
-- 12. UPCOMING FLIGHTS (Next 7 days)
-- ============================================
SELECT 
    f.flight_number,
    f.departure_point,
    f.arrival_point,
    f.flight_date,
    f.flight_time,
    a.code_number as aircraft,
    COUNT(fb.booking_id) as booked_passengers
FROM flights f
JOIN aircraft a ON f.aircraft_id = a.aircraft_id
LEFT JOIN flight_bookings fb ON f.flight_id = fb.flight_id
WHERE f.flight_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
GROUP BY f.flight_id, f.flight_number, f.departure_point, f.arrival_point, 
         f.flight_date, f.flight_time, a.code_number
ORDER BY f.flight_date, f.flight_time;

-- ============================================
-- 13. CHECK FOR OVERBOOKING
-- Identifies flights with more bookings than capacity
-- ============================================
SELECT 
    f.flight_number,
    f.departure_point,
    f.arrival_point,
    f.flight_date,
    a.passenger_capacity,
    COUNT(fb.booking_id) as total_bookings,
    COUNT(fb.booking_id) - a.passenger_capacity as overbooked_by
FROM flights f
JOIN aircraft a ON f.aircraft_id = a.aircraft_id
JOIN flight_bookings fb ON f.flight_id = fb.flight_id
GROUP BY f.flight_id, f.flight_number, f.departure_point, f.arrival_point, 
         f.flight_date, a.passenger_capacity
HAVING COUNT(fb.booking_id) > a.passenger_capacity
ORDER BY overbooked_by DESC;

-- ============================================
-- 14. PASSENGER CONTACT INFORMATION
-- Quick lookup for passenger contact details
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name,
    p.last_name,
    MAX(CASE WHEN pa.is_primary = true THEN pa.address_line END) as primary_address,
    MAX(CASE WHEN pa.is_primary = true THEN pa.city END) as city,
    MAX(CASE WHEN pa.is_primary = true THEN pa.country END) as country,
    MAX(CASE WHEN pp.phone_type = 'mobile' THEN pp.phone_number END) as phone_mobile,
    MAX(CASE WHEN pp.phone_type = 'home' THEN pp.phone_number END) as phone_home,
    MAX(CASE WHEN pp.phone_type = 'work' THEN pp.phone_number END) as phone_work,
    MAX(CASE WHEN pp.is_primary = true THEN pp.phone_number END) as primary_phone
FROM passengers p
LEFT JOIN passenger_phones pp ON p.passenger_id = pp.passenger_id
LEFT JOIN passenger_addresses pa ON p.passenger_id = pa.passenger_id
WHERE p.passenger_number = 'PAX001'
GROUP BY p.passenger_id, p.passenger_number, p.first_name, p.last_name;

-- ============================================
-- 15. FLIGHTS BY AIRCRAFT TYPE
-- Groups flights by aircraft model
-- ============================================
SELECT 
    a.brand,
    a.model,
    COUNT(DISTINCT f.flight_id) as total_flights,
    COUNT(DISTINCT fb.passenger_id) as unique_passengers,
    SUM(CASE WHEN f.status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
    SUM(CASE WHEN f.status = 'departed' THEN 1 ELSE 0 END) as departed
FROM aircraft a
LEFT JOIN flights f ON a.aircraft_id = f.aircraft_id
LEFT JOIN flight_bookings fb ON f.flight_id = fb.flight_id
GROUP BY a.brand, a.model
ORDER BY total_flights DESC;

-- ============================================
-- 16. ALL PHONE NUMBERS FOR ALL PASSENGERS
-- Shows complete phone directory
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name,
    p.last_name,
    pp.phone_type,
    pp.phone_number,
    pp.is_primary,
    CASE WHEN pp.is_primary = true THEN 'PRIMARY' ELSE '' END as primary_indicator
FROM passengers p
LEFT JOIN passenger_phones pp ON p.passenger_id = pp.passenger_id
ORDER BY p.passenger_number, pp.is_primary DESC, pp.phone_type;

-- ============================================
-- 17. PASSENGERS WITH PRIMARY CONTACT PHONE
-- Quick contact list with primary phone only
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name || ' ' || p.last_name as full_name,
    pp.phone_number as primary_phone,
    pp.phone_type as primary_phone_type
FROM passengers p
LEFT JOIN passenger_phones pp ON p.passenger_id = pp.passenger_id AND pp.is_primary = true
ORDER BY p.last_name, p.first_name;

-- ============================================
-- 18. PASSENGER PHONE COUNT
-- Shows how many phone numbers each passenger has registered
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name,
    p.last_name,
    COUNT(pp.phone_id) as total_phones,
    SUM(CASE WHEN pp.phone_type = 'mobile' THEN 1 ELSE 0 END) as mobile_count,
    SUM(CASE WHEN pp.phone_type = 'home' THEN 1 ELSE 0 END) as home_count,
    SUM(CASE WHEN pp.phone_type = 'work' THEN 1 ELSE 0 END) as work_count
FROM passengers p
LEFT JOIN passenger_phones pp ON p.passenger_id = pp.passenger_id
GROUP BY p.passenger_id, p.passenger_number, p.first_name, p.last_name
ORDER BY total_phones DESC;

-- ============================================
-- 19. ALL ADDRESSES FOR ALL PASSENGERS
-- Shows complete address directory
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name,
    p.last_name,
    pa.address_type,
    pa.address_line,
    pa.city,
    pa.country,
    pa.postal_code,
    pa.is_primary,
    CASE WHEN pa.is_primary = true THEN 'PRIMARY' ELSE '' END as primary_indicator
FROM passengers p
LEFT JOIN passenger_addresses pa ON p.passenger_id = pa.passenger_id
ORDER BY p.passenger_number, pa.is_primary DESC, pa.address_type;

-- ============================================
-- 20. PASSENGERS WITH PRIMARY ADDRESS
-- Quick address list with primary address only
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name || ' ' || p.last_name as full_name,
    pa.address_line,
    pa.city,
    pa.country,
    pa.postal_code
FROM passengers p
LEFT JOIN passenger_addresses pa ON p.passenger_id = pa.passenger_id AND pa.is_primary = true
ORDER BY p.last_name, p.first_name;

-- ============================================
-- 21. PASSENGER ADDRESS COUNT
-- Shows how many addresses each passenger has registered
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name,
    p.last_name,
    COUNT(pa.address_id) as total_addresses,
    SUM(CASE WHEN pa.address_type = 'home' THEN 1 ELSE 0 END) as home_count,
    SUM(CASE WHEN pa.address_type = 'work' THEN 1 ELSE 0 END) as work_count,
    SUM(CASE WHEN pa.address_type = 'billing' THEN 1 ELSE 0 END) as billing_count,
    SUM(CASE WHEN pa.address_type = 'other' THEN 1 ELSE 0 END) as other_count
FROM passengers p
LEFT JOIN passenger_addresses pa ON p.passenger_id = pa.passenger_id
GROUP BY p.passenger_id, p.passenger_number, p.first_name, p.last_name
ORDER BY total_addresses DESC;

-- ============================================
-- 22. COMPLETE PASSENGER PROFILE
-- Shows passenger with all phones and addresses
-- ============================================
SELECT 
    p.passenger_number,
    p.first_name || ' ' || p.last_name as full_name,
    pp.phone_type,
    pp.phone_number,
    pp.is_primary as phone_primary,
    pa.address_type,
    pa.address_line,
    pa.city,
    pa.country,
    pa.is_primary as address_primary
FROM passengers p
LEFT JOIN passenger_phones pp ON p.passenger_id = pp.passenger_id
LEFT JOIN passenger_addresses pa ON p.passenger_id = pa.passenger_id
WHERE p.passenger_number = 'PAX001'
ORDER BY pp.is_primary DESC, pa.is_primary DESC;
