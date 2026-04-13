from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    path('', views.index, name='index'),
    
    # Aircraft URLs
    path('aircraft/', views.AircraftListView.as_view(), name='aircraft_list'),
    path('aircraft/ajax/', views.aircraft_ajax, name='aircraft_ajax'),
    path('aircraft/<uuid:aircraft_id>/', views.AircraftDetailView.as_view(), name='aircraft_detail'),
    
    # Passenger URLs
    path('passengers/', views.PassengerListView.as_view(), name='passenger_list'),
    path('passengers/ajax/', views.passenger_ajax, name='passenger_ajax'),
    path('passengers/<uuid:passenger_id>/', views.PassengerDetailView.as_view(), name='passenger_detail'),
    
    # Flight URLs
    path('flights/', views.FlightListView.as_view(), name='flight_list'),
    path('flights/ajax/', views.flight_ajax, name='flight_ajax'),
    path('flights/<uuid:flight_id>/', views.FlightDetailView.as_view(), name='flight_detail'),
    path('flights/<uuid:flight_id>/bookings/ajax/', views.flight_bookings_ajax, name='flight_bookings_ajax'),
    
    # Airport URLs
    path('airports/', views.AirportListView.as_view(), name='airport_list'),
    path('airports/ajax/', views.airport_ajax, name='airport_ajax'),
    path('airports/<uuid:airport_id>/', views.AirportDetailView.as_view(), name='airport_detail'),
    
    # Booking URLs
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/ajax/', views.booking_ajax, name='booking_ajax'),
]
