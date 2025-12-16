from django.contrib import admin
from .models import Screen, Film, Showtime, Seat, Booking, BookingSeat

@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'type', 'number', 'seats']
    list_filter = ['type']

@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ['title', 'director', 'year', 'rating', 'is_new_release', 'is_classic', 'is_active']
    list_filter = ['rating', 'genre', 'is_new_release', 'is_classic', 'is_active', 'year']
    search_fields = ['title', 'director']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ['film', 'screen', 'date', 'time', 'price', 'available_seats', 'is_available']
    list_filter = ['date', 'screen', 'is_available']
    search_fields = ['film__title']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'screen', 'seat_type']
    list_filter = ['screen', 'seat_type']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'showtime', 'booking_date', 'total_price', 'status']
    list_filter = ['status', 'booking_date']
    search_fields = ['user__username', 'booking_id']
    readonly_fields = ['booking_id', 'booking_date']

@admin.register(BookingSeat)
class BookingSeatAdmin(admin.ModelAdmin):
    list_display = ['booking', 'seat', 'price']
    list_filter = ['booking__status']
