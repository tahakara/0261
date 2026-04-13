import uuid
from django.db import models
from django.core.validators import MinValueValidator


class Aircraft(models.Model):
    """Stores all aircraft in the company fleet with their specifications and maintenance status"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('repair', 'Repair'),
        ('inactive', 'Inactive'),
    ]
    
    aircraft_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_number = models.CharField(max_length=50, unique=True, verbose_name='Aircraft Code')
    brand = models.CharField(max_length=100, verbose_name='Brand')
    model = models.CharField(max_length=100, verbose_name='Model')
    passenger_capacity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Passenger Capacity'
    )
    range_km = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Range (km)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'aircraft'
        verbose_name = 'Aircraft'
        verbose_name_plural = 'Aircraft'
        ordering = ['code_number']
        indexes = [
            models.Index(fields=['code_number'], name='idx_aircraft_code'),
            models.Index(fields=['status'], name='idx_aircraft_status'),
        ]
    
    def __str__(self):
        return f"{self.code_number} - {self.brand} {self.model}"


class Passenger(models.Model):
    """Stores passenger information with unique company-wide identification"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    passenger_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    passenger_number = models.CharField(max_length=50, unique=True, verbose_name='Passenger Number')
    first_name = models.CharField(max_length=100, verbose_name='First Name')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Date of Birth')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='Gender')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'passengers'
        verbose_name = 'Passenger'
        verbose_name_plural = 'Passengers'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['passenger_number'], name='idx_passenger_number'),
            models.Index(fields=['last_name', 'first_name'], name='idx_passenger_name'),
        ]
    
    def __str__(self):
        return f"{self.passenger_number} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate passenger's age based on birth_date"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None


class PassengerPhone(models.Model):
    """Stores phone numbers for passengers with support for multiple phone types"""
    
    PHONE_TYPE_CHOICES = [
        ('home', 'Home'),
        ('mobile', 'Mobile'),
        ('work', 'Work'),
    ]
    
    phone_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.CASCADE,
        related_name='phones',
        verbose_name='Passenger'
    )
    phone_type = models.CharField(
        max_length=20,
        choices=PHONE_TYPE_CHOICES,
        verbose_name='Phone Type'
    )
    phone_number = models.CharField(max_length=20, verbose_name='Phone Number')
    is_primary = models.BooleanField(default=False, verbose_name='Is Primary')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'passenger_phones'
        verbose_name = 'Passenger Phone'
        verbose_name_plural = 'Passenger Phones'
        unique_together = [['passenger', 'phone_type']]
        indexes = [
            models.Index(fields=['passenger'], name='idx_pass_phone_pass'),
            models.Index(fields=['phone_type'], name='idx_pass_phone_type'),
        ]
    
    def __str__(self):
        return f"{self.passenger.passenger_number} - {self.get_phone_type_display()}: {self.phone_number}"


class PassengerAddress(models.Model):
    """Stores addresses for passengers with support for multiple address types"""
    
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('billing', 'Billing'),
        ('other', 'Other'),
    ]
    
    address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Passenger'
    )
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        verbose_name='Address Type'
    )
    address_line = models.TextField(verbose_name='Address')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='City')
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name='Country')
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Postal Code')
    is_primary = models.BooleanField(default=False, verbose_name='Is Primary')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'passenger_addresses'
        verbose_name = 'Passenger Address'
        verbose_name_plural = 'Passenger Addresses'
        indexes = [
            models.Index(fields=['passenger'], name='idx_pass_addr_pass'),
            models.Index(fields=['address_type'], name='idx_pass_addr_type'),
        ]
    
    def __str__(self):
        return f"{self.passenger.passenger_number} - {self.get_address_type_display()}"


class Airport(models.Model):
    """Stores airport information with IATA and ICAO codes"""
    
    AIRPORT_TYPE_CHOICES = [
        ('large_airport', 'Large Airport'),
        ('medium_airport', 'Medium Airport'),
        ('small_airport', 'Small Airport'),
        ('heliport', 'Heliport'),
        ('seaplane_base', 'Seaplane Base'),
        ('balloonport', 'Balloonport'),
        ('closed', 'Closed'),
    ]
    
    airport_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ident = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='OurAirports Identifier')
    airport_type = models.CharField(max_length=50, choices=AIRPORT_TYPE_CHOICES, blank=True, null=True, verbose_name='Airport Type')
    airport_name = models.CharField(max_length=200, verbose_name='Airport Name')
    latitude_deg = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, verbose_name='Latitude')
    longitude_deg = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True, verbose_name='Longitude')
    elevation_ft = models.IntegerField(blank=True, null=True, verbose_name='Elevation (ft)')
    continent = models.CharField(max_length=2, blank=True, null=True, verbose_name='Continent')
    iso_country = models.CharField(max_length=2, blank=True, null=True, verbose_name='ISO Country Code')
    iso_region = models.CharField(max_length=10, blank=True, null=True, verbose_name='ISO Region Code')
    municipality = models.CharField(max_length=100, blank=True, null=True, verbose_name='Municipality')
    scheduled_service = models.BooleanField(default=False, verbose_name='Scheduled Service')
    gps_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='GPS Code')
    iata_code = models.CharField(max_length=3, unique=True, blank=True, null=True, verbose_name='IATA Code')
    icao_code = models.CharField(max_length=4, unique=True, blank=True, null=True, verbose_name='ICAO Code')
    local_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='Local Code')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='City')
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name='Country')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'airports'
        verbose_name = 'Airport'
        verbose_name_plural = 'Airports'
        ordering = ['airport_name']
        indexes = [
            models.Index(fields=['iata_code'], name='idx_airport_iata'),
            models.Index(fields=['icao_code'], name='idx_airport_icao'),
            models.Index(fields=['city'], name='idx_airport_city'),
            models.Index(fields=['ident'], name='idx_airport_ident'),
            models.Index(fields=['airport_type'], name='idx_airport_type'),
        ]
    
    def __str__(self):
        if self.iata_code:
            return f"{self.iata_code} - {self.airport_name} ({self.municipality or self.city})"
        return f"{self.airport_name} ({self.municipality or self.city})"


class Flight(models.Model):
    """Stores flight schedules with departure/arrival information and aircraft assignments"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('arrived', 'Arrived'),
        ('cancelled', 'Cancelled'),
        ('delayed', 'Delayed'),
    ]
    
    flight_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flight_number = models.CharField(max_length=20, unique=True, verbose_name='Flight Number')
    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.RESTRICT,
        related_name='departures',
        verbose_name='Departure Airport'
    )
    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.RESTRICT,
        related_name='arrivals',
        verbose_name='Arrival Airport'
    )
    flight_date = models.DateField(verbose_name='Flight Date')
    flight_time = models.TimeField(verbose_name='Flight Time')
    aircraft = models.ForeignKey(
        Aircraft,
        on_delete=models.RESTRICT,
        related_name='flights',
        verbose_name='Aircraft'
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flights'
        verbose_name = 'Flight'
        verbose_name_plural = 'Flights'
        ordering = ['-flight_date', '-flight_time']
        indexes = [
            models.Index(fields=['flight_number'], name='idx_flight_number'),
            models.Index(fields=['flight_date'], name='idx_flight_date'),
            models.Index(fields=['aircraft'], name='idx_flight_aircraft'),
            models.Index(fields=['departure_airport'], name='idx_flight_dept'),
            models.Index(fields=['arrival_airport'], name='idx_flight_arr'),
        ]
    
    def __str__(self):
        return f"{self.flight_number} - {self.departure_airport.iata_code} to {self.arrival_airport.iata_code}"


class FlightBooking(models.Model):
    """Many-to-many relationship table linking passengers to their flights"""
    
    BOOKING_STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('boarded', 'Boarded'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Flight'
    )
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Passenger'
    )
    seat_number = models.CharField(max_length=10, blank=True, null=True, verbose_name='Seat Number')
    booking_status = models.CharField(
        max_length=50,
        choices=BOOKING_STATUS_CHOICES,
        default='confirmed',
        verbose_name='Booking Status'
    )
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name='Booking Date')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flight_bookings'
        verbose_name = 'Flight Booking'
        verbose_name_plural = 'Flight Bookings'
        unique_together = [
            ['flight', 'passenger'],
            ['flight', 'seat_number'],
        ]
        ordering = ['-booking_date']
        indexes = [
            models.Index(fields=['flight'], name='idx_booking_flight'),
            models.Index(fields=['passenger'], name='idx_booking_passenger'),
        ]
    
    def __str__(self):
        return f"{self.flight.flight_number} - {self.passenger.full_name} ({self.seat_number})"
