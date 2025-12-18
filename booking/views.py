from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Showtime, Seat, Booking, BookingSeat, Film
from django.utils import timezone
from datetime import timedelta
import json

def booking_view(request):  
    # Get all available films and showtimes for the booking page
    today = timezone.now().date()
    
    # Add date filtering similar to dashboard
    date_filter = request.GET.get("date", "today")
    genre_filter = request.GET.get("genre")
    
    # Search query
    query = request.GET.get("q")
    
    start_date = today
    end_date = None

    if date_filter == "today":
        start_date = today
        end_date = today
    elif date_filter == "tomorrow":
        start_date = today + timedelta(days=1)
        end_date = start_date
    elif date_filter == "this-week":
        start_date = today
        end_date = today + timedelta(days=6)
    elif date_filter == "next-week":
        start_date = today + timedelta(days=7)
        end_date = today + timedelta(days=13)
    elif date_filter:
        # Custom date (YYYY-MM-DD)
        try:
            start_date = end_date = timezone.datetime.strptime(
                date_filter, "%Y-%m-%d"
            ).date()
        except ValueError:
            pass

    # Build filter criteria
    showtime_filter = {
        "date__gte": start_date,
        "is_available": True,
        "film__is_active": True,
    }

    if end_date:
        showtime_filter["date__lte"] = end_date

    if genre_filter:
        showtime_filter["film__genre"] = genre_filter

    upcoming_showtimes = Showtime.objects.filter(**showtime_filter).select_related('film', 'screen').order_by('date', 'time')
    
    # If query for search
    if query:
        upcoming_showtimes = upcoming_showtimes.filter(
            film__title__icontains=query
        )
    
    # Group showtimes by film
    films_with_showtimes = {}
    for showtime in upcoming_showtimes:
        if showtime.film not in films_with_showtimes:
            films_with_showtimes[showtime.film] = []
        films_with_showtimes[showtime.film].append({
            'id': showtime.id,
            'time': showtime.time.strftime('%H:%M'),
            'date': showtime.date,
            'price': showtime.price,
            'screen': showtime.screen,
            'available_seats': showtime.available_seats
        })
    
    context = {
        'films_with_showtimes': films_with_showtimes,
        'current_step': 1,  # Step 1: Select Film & Showtime
        'selected_date': date_filter,
        'selected_genre': genre_filter or "",
        'query': query,
    }
    
    return render(request, 'booking/booking.html', context)

def select_seats(request, showtime_id):
    # Allow anyone to view seat selection (no login required yet)
    showtime = get_object_or_404(Showtime, id=showtime_id)
    screen = showtime.screen
    
    # Get all seats for this screen
    seats = Seat.objects.filter(screen=screen).order_by('row', 'number')
    
    # Get already booked seats for this showtime
    booked_seats = BookingSeat.objects.filter(
        booking__showtime=showtime
    ).values_list('seat_id', flat=True)
    
    context = {
        'showtime': showtime,
        'film': showtime.film,
        'screen': screen,
        'seats': seats,
        'booked_seats': list(booked_seats),
        'current_step': 2,  # Step 2: Select Seats
    }
    
    return render(request, 'booking/select_seats.html', context)

def proceed_to_login(request):
    # Store booking details in session before redirecting to login
    if request.method == 'POST':
        showtime_id = request.POST.get('showtime_id')
        selected_seats = request.POST.getlist('selected_seats')
        
        if not selected_seats:
            messages.error(request, 'Please select at least one seat.')
            return redirect('select_seats', showtime_id=showtime_id)
        
        # Store in session
        request.session['pending_booking'] = {
            'showtime_id': showtime_id,
            'selected_seats': selected_seats
        }
        
        # Redirect to login with next parameter
        return redirect(f'/accounts/login/?next=/booking/review-booking/')
    
    return redirect('booking')

@login_required
def review_booking(request):
    # Get booking details from session
    pending_booking = request.session.get('pending_booking')
    
    if not pending_booking:
        messages.error(request, 'No pending booking found. Please start over.')
        return redirect('booking')
    
    showtime = get_object_or_404(Showtime, id=pending_booking['showtime_id'])
    seats = Seat.objects.filter(id__in=pending_booking['selected_seats'])
    
    # Calculate total price
    total_price = len(pending_booking['selected_seats']) * showtime.price
    
    context = {
        'showtime': showtime,
        'film': showtime.film,
        'seats': seats,
        'total_price': total_price,
        'current_step': 3,  # Step 3: Review & Payment
    }
    
    return render(request, 'booking/review_booking.html', context)

@login_required
def confirm_booking(request):
    if request.method == 'POST':
        # Get booking details from session
        pending_booking = request.session.get('pending_booking')
        
        if not pending_booking:
            messages.error(request, 'No pending booking found. Please start over.')
            return redirect('booking')
        
        showtime = get_object_or_404(Showtime, id=pending_booking['showtime_id'])
        seats = Seat.objects.filter(id__in=pending_booking['selected_seats'])
        
        # Calculate total price
        total_price = len(pending_booking['selected_seats']) * showtime.price
        
        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            showtime=showtime,
            total_price=total_price,
            status='pending'
        )
        
        # Create booking seats
        for seat in seats:
            BookingSeat.objects.create(
                booking=booking,
                seat=seat,
                price=showtime.price
            )
        
        # Clear session
        if 'pending_booking' in request.session:
            del request.session['pending_booking']
        
        messages.success(request, f'Booking confirmed! Booking ID: {booking.booking_id}')
        return redirect('booking_success', booking_id=booking.booking_id)
    
    return redirect('booking')

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    context = {
        'booking': booking,
        'current_step': 4,  # Step 4: Confirmation
    }
    return render(request, 'booking/booking_success.html', context)

