from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

# Screen choices
SCREEN_TYPE_CHOICES = (
    (0, "Silver Screen"), 
    (1, "IMAX"), 
    (2, "Cabaret"), 
    (3, "VIP")
)

# Film rating choices
RATING_CHOICES = (
    ('G', 'General Audiences'),
    ('PG', 'Parental Guidance'),
    ('PG-13', 'Parents Strongly Cautioned'),
    ('15', '15 and Over'),
    ('18', '18 and Over'),
    ('R', 'Restricted'),
)

# Genre choices
GENRE_CHOICES = (
    ('action', 'Action'),
    ('adventure', 'Adventure'),
    ('comedy', 'Comedy'),
    ('drama', 'Drama'),
    ('horror', 'Horror'),
    ('romance', 'Romance'),
    ('sci-fi', 'Science Fiction'),
    ('thriller', 'Thriller'),
    ('documentary', 'Documentary'),
    ('animation', 'Animation'),
    ('family', 'Family'),
    ('fantasy', 'Fantasy'),
)

class Screen(models.Model):
    type = models.IntegerField(choices=SCREEN_TYPE_CHOICES, default=0)
    number = models.IntegerField(blank=False, null=False)
    seats = models.IntegerField(blank=False, null=False)
    
    class Meta:
        unique_together = ['type', 'number']
    
    def __str__(self):
        return f"{self.get_type_display()} {self.number}"

class Film(models.Model):
    title = models.CharField(max_length=200)
    director = models.CharField(max_length=100)
    cast = models.TextField(help_text="Main cast members, comma separated")
    year = models.DateField()
    duration = models.IntegerField(help_text="Duration in minutes")
    rating = models.CharField(max_length=5, choices=RATING_CHOICES, default='PG')
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='drama')
    synopsis = models.TextField(blank=True, null=True)
    poster_url = models.CharField(max_length=300, blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    is_new_release = models.BooleanField(default=True)
    is_classic = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # NEW FIELDS
    backdrop_url = models.CharField(max_length=300, blank=True, null=True)
    tmdb_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_poster_url(self):
        if self.poster_url:
            return self.poster_url
        return "https://via.placeholder.com/300x450/333/fff?text=No+Image"


class Showtime(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='showtimes')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['screen', 'date', 'time']
        ordering = ['date', 'time']
    
    def __str__(self):
        return f"{self.film.title} - {self.date} {self.time} - {self.screen}"
    
    @property
    def available_seats(self):
        """Calculate available seats for this showtime"""
        booked_seats = BookingSeat.objects.filter(
            booking__showtime=self
        ).count()
        return self.screen.seats - booked_seats

class Seat(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='seat_layout')
    row = models.CharField(max_length=2)  # A, B, C, etc.
    number = models.IntegerField()  # 1, 2, 3, etc.
    seat_type = models.CharField(max_length=20, default='standard')  # standard, premium, wheelchair
    
    class Meta:
        unique_together = ['screen', 'row', 'number']
        ordering = ['row', 'number']
    
    def __str__(self):
        return f"{self.row}{self.number}"

class Booking(models.Model):
    BOOKING_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.username}"
    
    @property
    def seat_numbers(self):
        """Return comma-separated list of seat numbers"""
        seats = self.booking_seats.all().order_by('seat__row', 'seat__number')
        return ', '.join([str(bs.seat) for bs in seats])

class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_seats')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        unique_together = ['booking', 'seat']
    
    def __str__(self):
        return f"{self.booking.booking_id} - {self.seat}"