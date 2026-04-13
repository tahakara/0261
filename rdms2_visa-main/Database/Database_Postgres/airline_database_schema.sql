-- Airline Management System Database Schema
-- PostgreSQL Implementation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Drop tables if they exist (for clean recreation)
DROP TABLE IF EXISTS flight_bookings CASCADE;
DROP TABLE IF EXISTS flights CASCADE;
DROP TABLE IF EXISTS airports CASCADE;
DROP TABLE IF EXISTS passenger_addresses CASCADE;
DROP TABLE IF EXISTS passenger_phones CASCADE;
DROP TABLE IF EXISTS aircraft CASCADE;
DROP TABLE IF EXISTS passengers CASCADE;

-- Aircraft Table
-- Stores information about all aircraft in the fleet
CREATE TABLE aircraft (
    aircraft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_number VARCHAR(50) UNIQUE NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    passenger_capacity INTEGER NOT NULL CHECK (passenger_capacity > 0),
    range_km INTEGER NOT NULL CHECK (range_km > 0),
    is_active BOOLEAN DEFAULT true NOT NULL,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'repair', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Passengers Table
-- Stores passenger information with unique company-wide passenger number
CREATE TABLE passengers (
    passenger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passenger_number VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Passenger Phones Table
-- Stores multiple phone numbers for each passenger
CREATE TABLE passenger_phones (
    phone_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passenger_id UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
    phone_type VARCHAR(20) NOT NULL CHECK (phone_type IN ('home', 'mobile', 'work')),
    phone_number VARCHAR(20) NOT NULL,
    is_primary BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(passenger_id, phone_type)
);

-- Passenger Addresses Table
-- Stores multiple addresses for each passenger
CREATE TABLE passenger_addresses (
    address_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    passenger_id UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
    address_type VARCHAR(20) NOT NULL CHECK (address_type IN ('home', 'work', 'billing', 'other')),
    address_line TEXT NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    is_primary BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Airports Table
-- Stores airport information with IATA and ICAO codes and extended OurAirports data
CREATE TABLE airports (
    airport_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ident VARCHAR(50) UNIQUE,
    airport_type VARCHAR(50) CHECK (airport_type IN ('large_airport', 'medium_airport', 'small_airport', 'heliport', 'seaplane_base', 'balloonport', 'closed')),
    airport_name VARCHAR(200) NOT NULL,
    latitude_deg DECIMAL(10, 6),
    longitude_deg DECIMAL(10, 6),
    elevation_ft INTEGER,
    continent VARCHAR(2),
    iso_country VARCHAR(2),
    iso_region VARCHAR(10),
    municipality VARCHAR(100),
    scheduled_service BOOLEAN DEFAULT false,
    gps_code VARCHAR(10),
    iata_code VARCHAR(3) UNIQUE,
    icao_code VARCHAR(4) UNIQUE,
    local_code VARCHAR(10),
    city VARCHAR(100),
    country VARCHAR(100),
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Flights Table
-- Stores flight information with departure/arrival airports and aircraft assignment
CREATE TABLE flights (
    flight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flight_number VARCHAR(20) UNIQUE NOT NULL,
    departure_airport_id UUID NOT NULL REFERENCES airports(airport_id) ON DELETE RESTRICT,
    arrival_airport_id UUID NOT NULL REFERENCES airports(airport_id) ON DELETE RESTRICT,
    flight_date DATE NOT NULL,
    flight_time TIME NOT NULL,
    aircraft_id UUID NOT NULL REFERENCES aircraft(aircraft_id) ON DELETE RESTRICT,
    status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'boarding', 'departed', 'arrived', 'cancelled', 'delayed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Flight Bookings Table (Many-to-Many relationship between Flights and Passengers)
-- Records which passengers are on which flights
CREATE TABLE flight_bookings (
    booking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flight_id UUID NOT NULL REFERENCES flights(flight_id) ON DELETE CASCADE,
    passenger_id UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
    seat_number VARCHAR(10),
    booking_status VARCHAR(50) DEFAULT 'confirmed' CHECK (booking_status IN ('confirmed', 'checked_in', 'boarded', 'cancelled', 'no_show')),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(flight_id, passenger_id),
    UNIQUE(flight_id, seat_number)
);

-- Indexes for better query performance
CREATE INDEX idx_aircraft_code ON aircraft(code_number);
CREATE INDEX idx_aircraft_status ON aircraft(status);
CREATE INDEX idx_passenger_number ON passengers(passenger_number);
CREATE INDEX idx_passenger_name ON passengers(last_name, first_name);
CREATE INDEX idx_passenger_phone_passenger ON passenger_phones(passenger_id);
CREATE INDEX idx_passenger_phone_type ON passenger_phones(phone_type);
CREATE INDEX idx_passenger_address_passenger ON passenger_addresses(passenger_id);
CREATE INDEX idx_passenger_address_type ON passenger_addresses(address_type);
CREATE INDEX idx_airport_iata ON airports(iata_code);
CREATE INDEX idx_airport_icao ON airports(icao_code);
CREATE INDEX idx_airport_city ON airports(city);
CREATE INDEX idx_airport_ident ON airports(ident);
CREATE INDEX idx_airport_type ON airports(airport_type);
CREATE INDEX idx_flight_number ON flights(flight_number);
CREATE INDEX idx_flight_date ON flights(flight_date);
CREATE INDEX idx_flight_aircraft ON flights(aircraft_id);
CREATE INDEX idx_flight_departure ON flights(departure_airport_id);
CREATE INDEX idx_flight_arrival ON flights(arrival_airport_id);
CREATE INDEX idx_booking_flight ON flight_bookings(flight_id);
CREATE INDEX idx_booking_passenger ON flight_bookings(passenger_id);

-- Trigger function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all tables
CREATE TRIGGER update_aircraft_updated_at BEFORE UPDATE ON aircraft
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_passengers_updated_at BEFORE UPDATE ON passengers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_passenger_phones_updated_at BEFORE UPDATE ON passenger_phones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_passenger_addresses_updated_at BEFORE UPDATE ON passenger_addresses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_airports_updated_at BEFORE UPDATE ON airports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_flights_updated_at BEFORE UPDATE ON flights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_flight_bookings_updated_at BEFORE UPDATE ON flight_bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE aircraft IS 'Stores all aircraft in the company fleet with their specifications and maintenance status';
COMMENT ON TABLE passengers IS 'Stores passenger information with unique company-wide identification';
COMMENT ON TABLE passenger_phones IS 'Stores phone numbers for passengers with support for multiple phone types';
COMMENT ON TABLE passenger_addresses IS 'Stores addresses for passengers with support for multiple address types';
COMMENT ON TABLE airports IS 'Stores airport information with IATA/ICAO codes and extended OurAirports data including coordinates and airport types';
COMMENT ON TABLE flights IS 'Stores flight schedules with departure/arrival airports and aircraft assignments';
COMMENT ON TABLE flight_bookings IS 'Many-to-many relationship table linking passengers to their flights';

COMMENT ON COLUMN aircraft.code_number IS 'Unique identification code for each aircraft';
COMMENT ON COLUMN aircraft.is_active IS 'Indicates if aircraft is currently in active service';
COMMENT ON COLUMN aircraft.status IS 'Current operational status: active, maintenance, repair, or inactive';
COMMENT ON COLUMN passengers.passenger_number IS 'Unique company-wide passenger identification number';
COMMENT ON COLUMN passengers.birth_date IS 'Date of birth of the passenger';
COMMENT ON COLUMN passengers.gender IS 'Gender: M (Male), F (Female), O (Other)';
COMMENT ON COLUMN passenger_phones.phone_type IS 'Type of phone number: home, mobile, or work';
COMMENT ON COLUMN passenger_phones.is_primary IS 'Indicates if this is the primary contact number for the passenger';
COMMENT ON COLUMN airports.ident IS 'OurAirports unique identifier';
COMMENT ON COLUMN airports.airport_type IS 'Type of airport: large_airport, medium_airport, small_airport, heliport, etc.';
COMMENT ON COLUMN airports.latitude_deg IS 'Latitude in decimal degrees';
COMMENT ON COLUMN airports.longitude_deg IS 'Longitude in decimal degrees';
COMMENT ON COLUMN airports.elevation_ft IS 'Elevation above sea level in feet';
COMMENT ON COLUMN airports.continent IS 'ISO continent code (2 letters)';
COMMENT ON COLUMN airports.iso_country IS 'ISO country code (2 letters)';
COMMENT ON COLUMN airports.iso_region IS 'ISO region code';
COMMENT ON COLUMN airports.municipality IS 'City/municipality where airport is located';
COMMENT ON COLUMN airports.scheduled_service IS 'Whether airport has scheduled airline service';
COMMENT ON COLUMN airports.gps_code IS 'GPS code for airport';
COMMENT ON COLUMN airports.iata_code IS '3-letter IATA code (e.g., IST, JFK)';
COMMENT ON COLUMN airports.icao_code IS '4-letter ICAO code (e.g., LTFM, KJFK)';
COMMENT ON COLUMN airports.local_code IS 'Local identifier code';
COMMENT ON COLUMN flights.departure_airport_id IS 'Airport where the flight departs from';
COMMENT ON COLUMN flights.arrival_airport_id IS 'Airport where the flight arrives at';
COMMENT ON COLUMN passenger_addresses.address_type IS 'Type of address: home, work, billing, or other';
COMMENT ON COLUMN passenger_addresses.is_primary IS 'Indicates if this is the primary address for the passenger';
COMMENT ON COLUMN flights.flight_number IS 'Unique flight identifier';
COMMENT ON COLUMN flight_bookings.booking_status IS 'Current status of the booking';
