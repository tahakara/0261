from django.test import TestCase
from django.utils import timezone
from datetime import date, time
from .models import Aircraft, Passenger, PassengerPhone, PassengerAddress, Flight, FlightBooking


class AircraftModelTest(TestCase):
    def setUp(self):
        self.aircraft = Aircraft.objects.create(
            code_number='AC001',
            brand='Boeing',
            model='737-800',
            passenger_capacity=189,
            range_km=5765,
            is_active=True,
            status='active'
        )
    
    def test_aircraft_creation(self):
        self.assertEqual(self.aircraft.code_number, 'AC001')
        self.assertEqual(self.aircraft.brand, 'Boeing')
        self.assertTrue(self.aircraft.is_active)
    
    def test_aircraft_str(self):
        self.assertEqual(str(self.aircraft), 'AC001 - Boeing 737-800')


class PassengerModelTest(TestCase):
    def setUp(self):
        self.passenger = Passenger.objects.create(
            passenger_number='P001',
            first_name='Ahmet',
            last_name='Yılmaz'
        )
    
    def test_passenger_creation(self):
        self.assertEqual(self.passenger.passenger_number, 'P001')
        self.assertEqual(self.passenger.first_name, 'Ahmet')
        self.assertEqual(self.passenger.last_name, 'Yılmaz')
    
    def test_passenger_full_name(self):
        self.assertEqual(self.passenger.full_name, 'Ahmet Yılmaz')
    
    def test_passenger_str(self):
        self.assertEqual(str(self.passenger), 'P001 - Ahmet Yılmaz')


class PassengerPhoneModelTest(TestCase):
    def setUp(self):
        self.passenger = Passenger.objects.create(
            passenger_number='P001',
            first_name='Ahmet',
            last_name='Yılmaz'
        )
        self.phone = PassengerPhone.objects.create(
            passenger=self.passenger,
            phone_type='mobile',
            phone_number='05551234567',
            is_primary=True
        )
    
    def test_phone_creation(self):
        self.assertEqual(self.phone.phone_number, '05551234567')
        self.assertEqual(self.phone.phone_type, 'mobile')
        self.assertTrue(self.phone.is_primary)


class FlightModelTest(TestCase):
    def setUp(self):
        self.aircraft = Aircraft.objects.create(
            code_number='AC001',
            brand='Boeing',
            model='737-800',
            passenger_capacity=189,
            range_km=5765
        )
        self.flight = Flight.objects.create(
            flight_number='TK001',
            departure_point='İstanbul',
            arrival_point='Ankara',
            flight_date=date(2026, 2, 20),
            flight_time=time(10, 30),
            aircraft=self.aircraft,
            status='scheduled'
        )
    
    def test_flight_creation(self):
        self.assertEqual(self.flight.flight_number, 'TK001')
        self.assertEqual(self.flight.departure_point, 'İstanbul')
        self.assertEqual(self.flight.arrival_point, 'Ankara')
    
    def test_flight_str(self):
        self.assertEqual(str(self.flight), 'TK001 - İstanbul to Ankara')


class FlightBookingModelTest(TestCase):
    def setUp(self):
        self.aircraft = Aircraft.objects.create(
            code_number='AC001',
            brand='Boeing',
            model='737-800',
            passenger_capacity=189,
            range_km=5765
        )
        self.flight = Flight.objects.create(
            flight_number='TK001',
            departure_point='İstanbul',
            arrival_point='Ankara',
            flight_date=date(2026, 2, 20),
            flight_time=time(10, 30),
            aircraft=self.aircraft
        )
        self.passenger = Passenger.objects.create(
            passenger_number='P001',
            first_name='Ahmet',
            last_name='Yılmaz'
        )
        self.booking = FlightBooking.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat_number='12A',
            booking_status='confirmed'
        )
    
    def test_booking_creation(self):
        self.assertEqual(self.booking.seat_number, '12A')
        self.assertEqual(self.booking.booking_status, 'confirmed')
    
    def test_booking_str(self):
        self.assertEqual(str(self.booking), 'TK001 - Ahmet Yılmaz (12A)')
