from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from django.http import JsonResponse
from django.urls import reverse
import json
from .models import Aircraft, Airport, Passenger, Flight, FlightBooking


def index(request):
    """Home page view"""
    context = {
        'total_aircraft': Aircraft.objects.count(),
        'total_airports': Airport.objects.count(),
        'total_passengers': Passenger.objects.count(),
        'total_flights': Flight.objects.count(),
        'upcoming_flights': Flight.objects.filter(status='scheduled').select_related('departure_airport', 'arrival_airport', 'aircraft').order_by('flight_date', 'flight_time')[:5],
        'active_aircraft': Aircraft.objects.filter(is_active=True, status='active').count(),
    }
    return render(request, 'flights/index.html', context)


class AircraftListView(ListView):
    """List all aircraft"""
    model = Aircraft
    template_name = 'flights/aircraft_list.html'
    context_object_name = 'aircraft_list'
    
    def get_queryset(self):
        queryset = Aircraft.objects.all()
        
        # Brand filter
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand=brand)
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Is active filter
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=(is_active == 'true'))
        
        # Search filter (code number or model)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(code_number__icontains=search) | 
                Q(model__icontains=search)
            )
        
        return queryset.order_by('code_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all aircraft (not paginated for statistics)
        all_aircraft = Aircraft.objects.all()
        
        # Get distinct brands for filter dropdown
        context['brands'] = Aircraft.objects.values_list('brand', flat=True).distinct().order_by('brand')
        
        # Pass current filter values to template
        context['current_brand'] = self.request.GET.get('brand', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_is_active'] = self.request.GET.get('is_active', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        # Build query string for pagination (without page parameter)
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_string'] = '&' + query_params.urlencode() if query_params else ''
        
        # Brand statistics
        brand_stats = all_aircraft.values('brand').annotate(count=Count('brand')).order_by('-count')
        context['brand_labels'] = json.dumps([item['brand'] for item in brand_stats])
        context['brand_data'] = json.dumps([item['count'] for item in brand_stats])
        
        # Capacity statistics (in ranges)
        capacity_ranges = {
            '150-200': all_aircraft.filter(passenger_capacity__gte=150, passenger_capacity__lt=200).count(),
            '200-250': all_aircraft.filter(passenger_capacity__gte=200, passenger_capacity__lt=250).count(),
            '250-300': all_aircraft.filter(passenger_capacity__gte=250, passenger_capacity__lt=300).count(),
            '300+': all_aircraft.filter(passenger_capacity__gte=300).count(),
        }
        context['capacity_labels'] = json.dumps(list(capacity_ranges.keys()))
        context['capacity_data'] = json.dumps(list(capacity_ranges.values()))
        
        # Range statistics (in km ranges)
        range_ranges = {
            '5000-7500': all_aircraft.filter(range_km__gte=5000, range_km__lt=7500).count(),
            '7500-10000': all_aircraft.filter(range_km__gte=7500, range_km__lt=10000).count(),
            '10000-12500': all_aircraft.filter(range_km__gte=10000, range_km__lt=12500).count(),
            '12500+': all_aircraft.filter(range_km__gte=12500).count(),
        }
        context['range_labels'] = json.dumps(list(range_ranges.keys()))
        context['range_data'] = json.dumps(list(range_ranges.values()))
        
        # Status statistics
        status_stats = all_aircraft.values('status').annotate(count=Count('status')).order_by('-count')
        status_display = {
            'active': 'Aktif',
            'maintenance': 'Bakımda',
            'repair': 'Tamirde',
            'inactive': 'Pasif'
        }
        context['status_labels'] = json.dumps([status_display.get(item['status'], item['status']) for item in status_stats])
        context['status_data'] = json.dumps([item['count'] for item in status_stats])
        
        return context


class AircraftDetailView(DetailView):
    """Detail view for a single aircraft"""
    model = Aircraft
    template_name = 'flights/aircraft_detail.html'
    context_object_name = 'aircraft'
    pk_url_kwarg = 'aircraft_id'


class PassengerListView(ListView):
    """List all passengers"""
    model = Passenger
    template_name = 'flights/passenger_list.html'
    context_object_name = 'passenger_list'
    
    def get_queryset(self):
        from datetime import date, timedelta
        queryset = Passenger.objects.all()
        
        # Gender filter
        gender = self.request.GET.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Age range filter (min_age, max_age)
        min_age = self.request.GET.get('min_age')
        max_age = self.request.GET.get('max_age')
        today = date.today()
        
        if min_age:
            try:
                min_age_int = int(min_age)
                max_birth_date = date(today.year - min_age_int, today.month, today.day)
                queryset = queryset.filter(birth_date__lte=max_birth_date)
            except ValueError:
                pass
        
        if max_age:
            try:
                max_age_int = int(max_age)
                min_birth_date = date(today.year - max_age_int - 1, today.month, today.day) + timedelta(days=1)
                queryset = queryset.filter(birth_date__gte=min_birth_date)
            except ValueError:
                pass
        
        # Exact age filter
        exact_age = self.request.GET.get('exact_age')
        if exact_age:
            try:
                age_int = int(exact_age)
                birth_year_start = today.year - age_int - 1
                birth_year_end = today.year - age_int
                queryset = queryset.filter(
                    birth_date__gte=date(birth_year_start, today.month, today.day),
                    birth_date__lte=date(birth_year_end, today.month, today.day)
                )
            except ValueError:
                pass
        
        # Registration date filter (from_date, to_date)
        from_date = self.request.GET.get('from_date')
        if from_date:
            queryset = queryset.filter(created_at__gte=from_date)
        
        to_date = self.request.GET.get('to_date')
        if to_date:
            queryset = queryset.filter(created_at__lte=to_date)
        
        # Search filter (first name or last name)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) |
                Q(passenger_number__icontains=search)
            )
        
        return queryset.order_by('last_name', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all passengers (not paginated for statistics)
        all_passengers = Passenger.objects.all()
        
        # Pass current filter values to template
        context['current_gender'] = self.request.GET.get('gender', '')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_min_age'] = self.request.GET.get('min_age', '')
        context['current_max_age'] = self.request.GET.get('max_age', '')
        context['current_exact_age'] = self.request.GET.get('exact_age', '')
        context['current_from_date'] = self.request.GET.get('from_date', '')
        context['current_to_date'] = self.request.GET.get('to_date', '')
        
        # Build query string for pagination (without page parameter)
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_string'] = '&' + query_params.urlencode() if query_params else ''
        
        # Gender statistics
        gender_stats = all_passengers.values('gender').annotate(count=Count('gender'))
        gender_display = {
            'M': 'Erkek',
            'F': 'Kadın',
            'O': 'Diğer',
            None: 'Belirtilmemiş'
        }
        gender_labels = []
        gender_data = []
        for item in gender_stats:
            gender_labels.append(gender_display.get(item['gender'], 'Belirtilmemiş'))
            gender_data.append(item['count'])
        context['gender_labels'] = json.dumps(gender_labels)
        context['gender_data'] = json.dumps(gender_data)
        
        # Age statistics (5-year ranges)
        from datetime import date
        today = date.today()
        
        age_ranges = {
            '0-24': 0,
            '25-29': 0,
            '30-34': 0,
            '35-39': 0,
            '40-44': 0,
            '45-49': 0,
            '50+': 0,
        }
        
        for passenger in all_passengers:
            if passenger.birth_date:
                age = today.year - passenger.birth_date.year - ((today.month, today.day) < (passenger.birth_date.month, passenger.birth_date.day))
                
                if age < 25:
                    age_ranges['0-24'] += 1
                elif age < 30:
                    age_ranges['25-29'] += 1
                elif age < 35:
                    age_ranges['30-34'] += 1
                elif age < 40:
                    age_ranges['35-39'] += 1
                elif age < 45:
                    age_ranges['40-44'] += 1
                elif age < 50:
                    age_ranges['45-49'] += 1
                else:
                    age_ranges['50+'] += 1
        
        context['age_labels'] = json.dumps(list(age_ranges.keys()))
        context['age_data'] = json.dumps(list(age_ranges.values()))
        
        return context


class PassengerDetailView(DetailView):
    """Detail view for a single passenger"""
    model = Passenger
    template_name = 'flights/passenger_detail.html'
    context_object_name = 'passenger'
    pk_url_kwarg = 'passenger_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookings'] = self.object.bookings.all().select_related('flight', 'flight__aircraft', 'flight__departure_airport', 'flight__arrival_airport')
        context['phones'] = self.object.phones.all()
        context['addresses'] = self.object.addresses.all()
        return context


class AirportListView(ListView):
    """List all airports"""
    model = Airport
    template_name = 'flights/airport_list.html'
    context_object_name = 'airport_list'
    
    def get_queryset(self):
        queryset = Airport.objects.all()
        
        # Airport type filter
        airport_type = self.request.GET.get('airport_type')
        if airport_type:
            queryset = queryset.filter(airport_type=airport_type)
        
        # Country filter
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(iso_country=country)
        
        # Search filter (name, IATA, ICAO)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(airport_name__icontains=search) |
                Q(iata_code__icontains=search) |
                Q(icao_code__icontains=search) |
                Q(municipality__icontains=search)
            )
        
        return queryset.order_by('iata_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get distinct airport types and countries for filters
        context['airport_types'] = Airport.objects.exclude(airport_type__isnull=True).values_list('airport_type', flat=True).distinct().order_by('airport_type')
        context['countries'] = Airport.objects.exclude(iso_country__isnull=True).values_list('iso_country', flat=True).distinct().order_by('iso_country')
        
        # Pass current filter values
        context['current_airport_type'] = self.request.GET.get('airport_type', '')
        context['current_country'] = self.request.GET.get('country', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        # Build query string for pagination (without page parameter)
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_string'] = '&' + query_params.urlencode() if query_params else ''
        
        return context


class AirportDetailView(DetailView):
    """Detail view for a single airport"""
    model = Airport
    template_name = 'flights/airport_detail.html'
    context_object_name = 'airport'
    pk_url_kwarg = 'airport_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departures'] = self.object.departures.all().select_related('arrival_airport', 'aircraft').order_by('-flight_date', '-flight_time')[:10]
        context['arrivals'] = self.object.arrivals.all().select_related('departure_airport', 'aircraft').order_by('-flight_date', '-flight_time')[:10]
        return context


class FlightListView(ListView):
    """List all flights"""
    model = Flight
    template_name = 'flights/flight_list.html'
    context_object_name = 'flight_list'
    
    def get_queryset(self):
        # Return empty queryset since we're using AJAX/DataTables
        # This prevents loading all flights on initial page load
        return Flight.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get airports and aircraft for filter dropdowns - optimized with only necessary fields
        context['airports'] = Airport.objects.filter(is_active=True).only('airport_id', 'iata_code', 'city').order_by('iata_code')
        context['aircrafts'] = Aircraft.objects.filter(is_active=True).only('aircraft_id', 'code_number').order_by('code_number')
        
        # Pass current filter values
        context['current_status'] = self.request.GET.get('status', '')
        context['current_departure'] = self.request.GET.get('departure', '')
        context['current_arrival'] = self.request.GET.get('arrival', '')
        context['current_aircraft'] = self.request.GET.get('aircraft', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context


class FlightDetailView(DetailView):
    """Detail view for a single flight"""
    model = Flight
    template_name = 'flights/flight_detail.html'
    context_object_name = 'flight'
    pk_url_kwarg = 'flight_id'
    
    def get_queryset(self):
        return Flight.objects.select_related(
            'aircraft',
            'departure_airport',
            'arrival_airport'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only pass booking count, not all bookings (they will be loaded via AJAX)
        context['bookings'] = self.object.bookings
        context['available_seats'] = self.object.aircraft.passenger_capacity - self.object.bookings.count()
        
        # Add airport coordinates for map visualization
        context['departure_lat'] = float(self.object.departure_airport.latitude_deg) if self.object.departure_airport.latitude_deg else None
        context['departure_lon'] = float(self.object.departure_airport.longitude_deg) if self.object.departure_airport.longitude_deg else None
        context['arrival_lat'] = float(self.object.arrival_airport.latitude_deg) if self.object.arrival_airport.latitude_deg else None
        context['arrival_lon'] = float(self.object.arrival_airport.longitude_deg) if self.object.arrival_airport.longitude_deg else None
        
        return context


class BookingListView(ListView):
    """List all bookings"""
    model = FlightBooking
    template_name = 'flights/booking_list.html'
    context_object_name = 'booking_list'
    
    def get_queryset(self):
        queryset = FlightBooking.objects.all().select_related('flight', 'passenger', 'flight__aircraft', 'flight__departure_airport', 'flight__arrival_airport')
        
        # Booking status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(booking_status=status)
        
        # Flight filter
        flight = self.request.GET.get('flight')
        if flight:
            queryset = queryset.filter(flight_id=flight)
        
        # Passenger filter
        passenger = self.request.GET.get('passenger')
        if passenger:
            queryset = queryset.filter(passenger_id=passenger)
        
        # Search filter (booking number)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(booking_number__icontains=search)
        
        return queryset.order_by('-booking_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get flights and passengers for filter dropdowns
        context['flights'] = Flight.objects.all().select_related('departure_airport', 'arrival_airport').order_by('-flight_date')
        context['passengers'] = Passenger.objects.all().order_by('last_name', 'first_name')
        
        # Pass current filter values
        context['current_status'] = self.request.GET.get('status', '')
        context['current_flight'] = self.request.GET.get('flight', '')
        context['current_passenger'] = self.request.GET.get('passenger', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        # Build query string for pagination (without page parameter)
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')
        context['query_string'] = '&' + query_params.urlencode() if query_params else ''
        
        return context


# DataTables AJAX endpoints for server-side processing

def aircraft_ajax(request):
    """AJAX endpoint for Aircraft DataTable"""
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    
    # Apply filters from filter form
    queryset = Aircraft.objects.all()
    
    brand = request.GET.get('brand')
    if brand:
        queryset = queryset.filter(brand=brand)
    
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)
    
    is_active = request.GET.get('is_active')
    if is_active:
        queryset = queryset.filter(is_active=(is_active == 'true'))
    
    search = request.GET.get('search_form')
    if search:
        queryset = queryset.filter(
            Q(code_number__icontains=search) | 
            Q(model__icontains=search)
        )
    
    # Apply DataTables search
    if search_value:
        queryset = queryset.filter(
            Q(code_number__icontains=search_value) |
            Q(brand__icontains=search_value) |
            Q(model__icontains=search_value)
        )
    
    # Total records
    records_total = Aircraft.objects.count()
    records_filtered = queryset.count()
    
    # Apply ordering
    order_column_index = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')
    
    order_columns = ['code_number', 'brand', 'model', 'passenger_capacity', 'range_km', 'status', None]
    if order_column_index < len(order_columns) and order_columns[order_column_index]:
        order_field = order_columns[order_column_index]
        if order_dir == 'desc':
            order_field = '-' + order_field
        queryset = queryset.order_by(order_field)
    else:
        queryset = queryset.order_by('code_number')
    
    # Apply pagination
    queryset = queryset[start:start + length]
    
    # Build data
    data = []
    for aircraft in queryset:
        detail_url = reverse('flights:aircraft_detail', kwargs={'aircraft_id': str(aircraft.aircraft_id)})
        data.append([
            aircraft.code_number,
            aircraft.brand,
            aircraft.model,
            aircraft.passenger_capacity,
            aircraft.range_km,
            aircraft.get_status_display(),
            f'<a href="{detail_url}" class="btn btn-primary btn-sm">Detay</a>'
        ])
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data
    })


def passenger_ajax(request):
    """AJAX endpoint for Passenger DataTable"""
    from datetime import date, timedelta
    
    today = date.today()
    
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    
    # Apply filters from filter form
    queryset = Passenger.objects.all()
    
    gender = request.GET.get('gender')
    if gender:
        queryset = queryset.filter(gender=gender)
    
    # Age filters
    min_age = request.GET.get('min_age')
    max_age = request.GET.get('max_age')
    exact_age = request.GET.get('exact_age')
    
    today = date.today()
    
    if exact_age:
        try:
            exact_age_int = int(exact_age)
            min_birth_date = date(today.year - exact_age_int - 1, today.month, today.day) + timedelta(days=1)
            max_birth_date = date(today.year - exact_age_int, today.month, today.day)
            queryset = queryset.filter(birth_date__gte=min_birth_date, birth_date__lte=max_birth_date)
        except (ValueError, TypeError):
            pass
    else:
        if min_age:
            try:
                min_age_int = int(min_age)
                max_birth_date = date(today.year - min_age_int, today.month, today.day)
                queryset = queryset.filter(birth_date__lte=max_birth_date)
            except (ValueError, TypeError):
                pass
        
        if max_age:
            try:
                max_age_int = int(max_age)
                min_birth_date = date(today.year - max_age_int - 1, today.month, today.day) + timedelta(days=1)
                queryset = queryset.filter(birth_date__gte=min_birth_date)
            except (ValueError, TypeError):
                pass
    
    # Date filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if from_date:
        queryset = queryset.filter(created_at__date__gte=from_date)
    
    if to_date:
        queryset = queryset.filter(created_at__date__lte=to_date)
    
    search_form = request.GET.get('search_form')
    if search_form:
        queryset = queryset.filter(
            Q(first_name__icontains=search_form) |
            Q(last_name__icontains=search_form) |
            Q(passenger_number__icontains=search_form)
        )
    
    # Apply DataTables search
    if search_value:
        queryset = queryset.filter(
            Q(first_name__icontains=search_value) |
            Q(last_name__icontains=search_value) |
            Q(passenger_number__icontains=search_value)
        )
    
    # Total records
    records_total = Passenger.objects.count()
    records_filtered = queryset.count()
    
    # Apply ordering
    order_column_index = int(request.GET.get('order[0][column]', 1))
    order_dir = request.GET.get('order[0][dir]', 'asc')
    
    order_columns = [None, 'first_name', 'last_name', 'birth_date', 'gender', None]
    if order_column_index < len(order_columns) and order_columns[order_column_index]:
        order_field = order_columns[order_column_index]
        if order_dir == 'desc':
            order_field = '-' + order_field
        queryset = queryset.order_by(order_field)
    else:
        queryset = queryset.order_by('first_name', 'last_name')
    
    # Apply pagination
    queryset = queryset[start:start + length]
    
    # Build data
    data = []
    for passenger in queryset:
        age = None
        if passenger.birth_date:
            age = today.year - passenger.birth_date.year - ((today.month, today.day) < (passenger.birth_date.month, passenger.birth_date.day))
        
        # Safe full name for URL encoding
        full_name_safe = f"{passenger.first_name} {passenger.last_name}".replace(' ', '+')
        detail_url = reverse('flights:passenger_detail', kwargs={'passenger_id': str(passenger.passenger_id)})
        
        data.append([
            f'<img src="https://ui-avatars.com/api/?name={full_name_safe}&background=random" alt="Avatar" style="width:40px;height:40px;border-radius:50%;">',
            passenger.first_name,
            passenger.last_name,
            f'{age} yaş' if age else '-',
            passenger.get_gender_display() if passenger.gender else '-',
            f'<a href="{detail_url}" class="btn btn-primary btn-sm">Detay</a>'
        ])
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data
    })


def airport_ajax(request):
    """AJAX endpoint for Airport DataTable"""
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    
    # Apply filters from filter form
    queryset = Airport.objects.all()
    
    airport_type = request.GET.get('airport_type')
    if airport_type:
        queryset = queryset.filter(airport_type=airport_type)
    
    country = request.GET.get('country')
    if country:
        queryset = queryset.filter(country=country)
    
    search_form = request.GET.get('search_form')
    if search_form:
        queryset = queryset.filter(
            Q(iata_code__icontains=search_form) |
            Q(icao_code__icontains=search_form) |
            Q(airport_name__icontains=search_form) |
            Q(city__icontains=search_form)
        )
    
    # Apply DataTables search
    if search_value:
        queryset = queryset.filter(
            Q(iata_code__icontains=search_value) |
            Q(icao_code__icontains=search_value) |
            Q(airport_name__icontains=search_value) |
            Q(city__icontains=search_value) |
            Q(country__icontains=search_value)
        )
    
    # Total records
    records_total = Airport.objects.count()
    records_filtered = queryset.count()
    
    # Apply ordering
    order_column_index = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')
    
    order_columns = ['iata_code', 'icao_code', 'airport_name', 'city', 'country', 'is_active', None]
    if order_column_index < len(order_columns) and order_columns[order_column_index]:
        order_field = order_columns[order_column_index]
        if order_dir == 'desc':
            order_field = '-' + order_field
        queryset = queryset.order_by(order_field)
    else:
        queryset = queryset.order_by('iata_code')
    
    # Apply pagination
    queryset = queryset[start:start + length]
    
    # Build data
    data = []
    for airport in queryset:
        detail_url = reverse('flights:airport_detail', kwargs={'airport_id': str(airport.airport_id)})
        data.append([
            airport.iata_code or '-',
            airport.icao_code or '-',
            airport.airport_name,
            airport.city,
            airport.country,
            '✅ Aktif' if airport.is_active else '❌ Pasif',
            f'<a href="{detail_url}" class="btn btn-primary btn-sm">Detay</a>'
        ])
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data
    })


def flight_ajax(request):
    """AJAX endpoint for Flight DataTable"""
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    
    # Base queryset with optimized select_related
    base_queryset = Flight.objects.select_related('aircraft', 'departure_airport', 'arrival_airport')
    
    # Apply filters from filter form
    queryset = base_queryset
    
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)
    
    departure = request.GET.get('departure')
    if departure:
        queryset = queryset.filter(departure_airport_id=departure)
    
    arrival = request.GET.get('arrival')
    if arrival:
        queryset = queryset.filter(arrival_airport_id=arrival)
    
    aircraft = request.GET.get('aircraft')
    if aircraft:
        queryset = queryset.filter(aircraft_id=aircraft)
    
    search_form = request.GET.get('search_form')
    if search_form:
        queryset = queryset.filter(flight_number__icontains=search_form)
    
    # Store count after form filters but before DataTables search
    records_total = base_queryset.count()
    records_filtered = queryset.count()
    
    # Apply DataTables search
    if search_value:
        queryset = queryset.filter(
            Q(flight_number__icontains=search_value) |
            Q(departure_airport__iata_code__icontains=search_value) |
            Q(arrival_airport__iata_code__icontains=search_value) |
            Q(aircraft__code_number__icontains=search_value)
        )
        records_filtered = queryset.count()
    
    # Apply ordering
    order_column_index = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')
    
    order_columns = ['flight_number', 'departure_airport__iata_code', 'arrival_airport__iata_code', 'flight_date', 'flight_time', 'aircraft__code_number', 'status', None]
    if order_column_index < len(order_columns) and order_columns[order_column_index]:
        order_field = order_columns[order_column_index]
        if order_dir == 'desc':
            order_field = '-' + order_field
        queryset = queryset.order_by(order_field)
    else:
        queryset = queryset.order_by('flight_number')
    
    # Apply pagination
    queryset = queryset[start:start + length]
    
    # Build data
    data = []
    for flight in queryset:
        detail_url = reverse('flights:flight_detail', kwargs={'flight_id': str(flight.flight_id)})
        data.append([
            flight.flight_number,
            f'{flight.departure_airport.iata_code} - {flight.departure_airport.city}',
            f'{flight.arrival_airport.iata_code} - {flight.arrival_airport.city}',
            str(flight.flight_date),
            str(flight.flight_time),
            flight.aircraft.code_number,
            flight.get_status_display(),
            f'<a href="{detail_url}" class="btn btn-primary btn-sm">Detay</a>'
        ])
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data
    })


def booking_ajax(request):
    """AJAX endpoint for Booking DataTable"""
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    
    # Apply filters from filter form
    queryset = FlightBooking.objects.all().select_related('flight', 'passenger', 'flight__aircraft', 'flight__departure_airport', 'flight__arrival_airport')
    
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(booking_status=status)
    
    flight = request.GET.get('flight')
    if flight:
        queryset = queryset.filter(flight_id=flight)
    
    passenger = request.GET.get('passenger')
    if passenger:
        queryset = queryset.filter(passenger_id=passenger)
    
    search_form = request.GET.get('search_form')
    if search_form:
        queryset = queryset.filter(booking_reference__icontains=search_form)
    
    # Apply DataTables search
    if search_value:
        queryset = queryset.filter(
            Q(booking_reference__icontains=search_value) |
            Q(flight__flight_number__icontains=search_value) |
            Q(passenger__first_name__icontains=search_value) |
            Q(passenger__last_name__icontains=search_value)
        )
    
    # Total records
    records_total = FlightBooking.objects.count()
    records_filtered = queryset.count()
    
    # Apply ordering
    order_column_index = int(request.GET.get('order[0][column]', 7))
    order_dir = request.GET.get('order[0][dir]', 'desc')
    
    order_columns = ['flight__flight_number', 'passenger__first_name', None, None, 'flight__flight_date', 'seat_number', 'booking_status', 'booking_date']
    if order_column_index < len(order_columns) and order_columns[order_column_index]:
        order_field = order_columns[order_column_index]
        if order_dir == 'desc':
            order_field = '-' + order_field
        queryset = queryset.order_by(order_field)
    else:
        queryset = queryset.order_by('-booking_date')
    
    # Apply pagination
    queryset = queryset[start:start + length]
    
    # Build data
    data = []
    for booking in queryset:
        flight_url = reverse('flights:flight_detail', kwargs={'flight_id': str(booking.flight.flight_id)})
        passenger_url = reverse('flights:passenger_detail', kwargs={'passenger_id': str(booking.passenger.passenger_id)})
        data.append([
            f'<a href="{flight_url}">{booking.flight.flight_number}</a>',
            f'<a href="{passenger_url}">{booking.passenger.full_name}</a>',
            f'{booking.flight.departure_airport.iata_code} - {booking.flight.departure_airport.city}',
            f'{booking.flight.arrival_airport.iata_code} - {booking.flight.arrival_airport.city}',
            str(booking.flight.flight_date),
            booking.seat_number or 'Atanmadı',
            booking.get_booking_status_display(),
            booking.booking_date.strftime('%d.%m.%Y %H:%M')
        ])
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data
    })


def flight_bookings_ajax(request, flight_id):
    """AJAX endpoint for Flight Bookings DataTable"""
    flight = get_object_or_404(Flight, flight_id=flight_id)
    
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')
    
    # Get bookings for this flight
    queryset = FlightBooking.objects.filter(flight=flight).select_related('passenger')
    
    # Apply DataTables search
    if search_value:
        queryset = queryset.filter(
            Q(passenger__first_name__icontains=search_value) |
            Q(passenger__last_name__icontains=search_value) |
            Q(passenger__passenger_number__icontains=search_value) |
            Q(seat_number__icontains=search_value) |
            Q(booking_status__icontains=search_value)
        )
    
    # Total records
    records_total = FlightBooking.objects.filter(flight=flight).count()
    records_filtered = queryset.count()
    
    # Apply ordering
    order_column_index = int(request.GET.get('order[0][column]', 4))
    order_dir = request.GET.get('order[0][dir]', 'desc')
    
    order_columns = ['passenger__passenger_number', 'passenger__first_name', 'seat_number', 'booking_status', 'booking_date']
    if order_column_index < len(order_columns) and order_columns[order_column_index]:
        order_field = order_columns[order_column_index]
        if order_dir == 'desc':
            order_field = '-' + order_field
        queryset = queryset.order_by(order_field)
    else:
        queryset = queryset.order_by('-booking_date')
    
    # Apply pagination
    queryset = queryset[start:start + length]
    
    # Build data
    data = []
    for booking in queryset:
        passenger_url = reverse('flights:passenger_detail', kwargs={'passenger_id': str(booking.passenger.passenger_id)})
        data.append([
            f'<a href="{passenger_url}">{booking.passenger.passenger_number}</a>',
            f'<a href="{passenger_url}">{booking.passenger.full_name}</a>',
            booking.seat_number if booking.seat_number else 'Atanmadı',
            booking.get_booking_status_display(),
            booking.booking_date.strftime('%Y-%m-%d')
        ])
    
    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data
    })

