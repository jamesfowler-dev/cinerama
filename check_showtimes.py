import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinerama.settings')
django.setup()

from booking.models import Showtime
from django.utils import timezone

today = timezone.now().date()

print(f'Today: {today}')
print(f'Total showtimes: {Showtime.objects.count()}')
print(f'Today: {Showtime.objects.filter(date=today).count()}')
print(f'Tomorrow: {Showtime.objects.filter(date=today + timezone.timedelta(days=1)).count()}')
print(f'This week (next 7 days): {Showtime.objects.filter(date__gte=today, date__lte=today + timezone.timedelta(days=6)).count()}')
print(f'Next week (day 7-13): {Showtime.objects.filter(date__gte=today + timezone.timedelta(days=7), date__lte=today + timezone.timedelta(days=13)).count()}')

print('\nAll showtime dates:')
for st in Showtime.objects.all().order_by('date'):
    print(f'  {st.date} - {st.time} - {st.film.title} - Available: {st.is_available}')
