import os
import django

essential = 'cinerama.settings'
if os.environ.get('DJANGO_SETTINGS_MODULE') != essential:
    os.environ['DJANGO_SETTINGS_MODULE'] = essential

django.setup()

from django.conf import settings  # noqa: E402
# Allow the test client host used by Django's test Client
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import Client  # noqa: E402
from django.contrib.auth.models import User
from booking.models import Film
from django.utils import timezone
from datetime import date

# Helpers
USERNAME = 'teststaff'
PASSWORD = 'testpass'
TMDB_ID = 999999999
VIDEO_ID = 'abc123xyz'

# Create staff user if not exists
user, created = User.objects.get_or_create(username=USERNAME)
if created:
    user.is_staff = True
    user.set_password(PASSWORD)
    user.save()
else:
    # Ensure password set to known value for tests
    user.set_password(PASSWORD)
    user.is_staff = True
    user.save()

# Create or update a Film with TMDB_ID
film, _ = Film.objects.update_or_create(
    tmdb_id=TMDB_ID,
    defaults={
        'title': 'Test Film for Flow',
        'director': 'Director Name',
        'cast': 'Actor One, Actor Two',
        'year': date(2000, 1, 1),
        'duration': 120,
    }
)

client = Client()
logged_in = client.login(username=USERNAME, password=PASSWORD)
print('Logged in:', logged_in)

# Test GET-based select_trailer URL, which should redirect to ai_rating
select_url = f'/add-movie/trailer/select/{TMDB_ID}/{VIDEO_ID}/'
resp = client.get(select_url, follow=True)
print('\nGET select_trailer ->')
print('Requested URL:', select_url)
print('Final status code:', resp.status_code)
print('Redirect chain:')
for r, status in resp.redirect_chain:
    print('  ->', r, status)
print('Final path (approx):', resp.request.get('PATH_INFO'))
print('Response snippet:')
print(resp.content[:800].decode(errors='ignore'))

# Test POST-based choose_trailer URL, which should now redirect to ai_rating
choose_url = f'/add-movie/trailer/{TMDB_ID}/'
resp2 = client.post(choose_url, {'video_id': VIDEO_ID}, follow=True)
print('\nPOST choose_trailer ->')
print('Requested URL:', choose_url)
print('Final status code:', resp2.status_code)
print('Redirect chain:')
for r, status in resp2.redirect_chain:
    print('  ->', r, status)
print('Final path (approx):', resp2.request.get('PATH_INFO'))
print('Response snippet:')
print(resp2.content[:800].decode(errors='ignore'))

print('\nDone')
