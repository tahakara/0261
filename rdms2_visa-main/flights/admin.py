from django.contrib import admin
from .models import Aircraft, Airport, Passenger, PassengerPhone, PassengerAddress, Flight, FlightBooking


class PassengerPhoneInline(admin.TabularInline):
    model = PassengerPhone
    extra = 1
    fields = ['phone_type', 'phone_number', 'is_primary']


class PassengerAddressInline(admin.TabularInline):
    model = PassengerAddress
    extra = 1
    fields = ['address_type', 'address_line', 'city', 'country', 'postal_code', 'is_primary']


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ['code_number', 'brand', 'model', 'passenger_capacity', 'range_km', 'status', 'is_active']
    list_filter = ['status', 'is_active', 'brand']
    search_fields = ['code_number', 'brand', 'model']
    readonly_fields = ['aircraft_id', 'created_at', 'updated_at']
    fieldsets = [
        ('Aircraft Information', {
            'fields': ['code_number', 'brand', 'model']
        }),
        ('Specifications', {
            'fields': ['passenger_capacity', 'range_km']
        }),
        ('Status', {
            'fields': ['is_active', 'status']
        }),
        ('System Information', {
            'fields': ['aircraft_id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['passenger_number', 'first_name', 'last_name', 'created_at']
    search_fields = ['passenger_number', 'first_name', 'last_name']
    readonly_fields = ['passenger_id', 'created_at', 'updated_at']
    inlines = [PassengerPhoneInline, PassengerAddressInline]
    fieldsets = [
        ('Passenger Information', {
            'fields': ['passenger_number', 'first_name', 'last_name']
        }),
        ('System Information', {
            'fields': ['passenger_id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(PassengerPhone)
class PassengerPhoneAdmin(admin.ModelAdmin):
    list_display = ['passenger', 'phone_type', 'phone_number', 'is_primary']
    list_filter = ['phone_type', 'is_primary']
    search_fields = ['passenger__passenger_number', 'passenger__first_name', 'passenger__last_name', 'phone_number']
    readonly_fields = ['phone_id', 'created_at', 'updated_at']


@admin.register(PassengerAddress)
class PassengerAddressAdmin(admin.ModelAdmin):
    list_display = ['passenger', 'address_type', 'city', 'country', 'is_primary']
    list_filter = ['address_type', 'is_primary', 'country']
    search_fields = ['passenger__passenger_number', 'passenger__first_name', 'passenger__last_name', 'city', 'country']
    readonly_fields = ['address_id', 'created_at', 'updated_at']


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    """Admin interface for Airport model"""
    list_display = ['iata_code', 'icao_code', 'airport_name', 'city', 'country', 'is_active']
    list_filter = ['is_active', 'country', 'city']
    search_fields = ['airport_name', 'iata_code', 'icao_code', 'city', 'country']
    list_editable = ['is_active']
    ordering = ['iata_code']
    readonly_fields = ['airport_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Airport Information', {
            'fields': ('airport_name', 'city', 'country')
        }),
        ('Codes', {
            'fields': ('iata_code', 'icao_code')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('airport_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'departure_airport', 'arrival_airport', 'flight_date', 'flight_time', 'aircraft', 'status']
    list_filter = ['status', 'flight_date', 'departure_airport__city', 'arrival_airport__city']
    search_fields = ['flight_number', 'departure_airport__airport_name', 'arrival_airport__airport_name', 'departure_airport__iata_code', 'arrival_airport__iata_code', 'aircraft__code_number']
    readonly_fields = ['flight_id', 'created_at', 'updated_at']
    date_hierarchy = 'flight_date'
    fieldsets = [
        ('Flight Information', {
            'fields': ['flight_number', 'aircraft']
        }),
        ('Route', {
            'fields': ['departure_airport', 'arrival_airport']
        }),
        ('Schedule', {
            'fields': ['flight_date', 'flight_time', 'status']
        }),
        ('System Information', {
            'fields': ['flight_id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(FlightBooking)
class FlightBookingAdmin(admin.ModelAdmin):
    list_display = ['flight', 'passenger', 'seat_number', 'booking_status', 'booking_date']
    list_filter = ['booking_status', 'booking_date']
    search_fields = ['flight__flight_number', 'passenger__passenger_number', 'passenger__first_name', 'passenger__last_name', 'seat_number']
    readonly_fields = ['booking_id', 'booking_date', 'created_at', 'updated_at']
    date_hierarchy = 'booking_date'
    fieldsets = [
        ('Booking Information', {
            'fields': ['flight', 'passenger', 'seat_number']
        }),
        ('Status', {
            'fields': ['booking_status']
        }),
        ('System Information', {
            'fields': ['booking_id', 'booking_date', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


# Customize admin site header and title
admin.site.site_header = 'Airline Management System'
admin.site.site_title = 'Airline Admin'
admin.site.index_title = 'Welcome to Airline Management System'
