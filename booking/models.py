from django.db import models
from django.contrib.auth.models import User



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# DO NOT MIGRATE UNTIL WE HAVE THE DASHBOARD APP, SOME MODELS WILL LIVE THERE
# 1!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! I JUST NEED YOUR ENV.PY TO USE python manage.py startapp
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Create your models here.

SCREEN_TYPE_CHOICES = ((0, "Silver Screen"), (1, "IMAX"), (2, "Cabaret"), (3, "VIP"))

class Screen(models.Model):
    type = models.IntegerField(choices=SCREEN_TYPE_CHOICES, default=0)
    number = models.IntegerField(blank=False, null=False)
    seats = models.IntegerField(blank=False, null=False)
# more to be added

class Film(models.Model):
    title = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    cast = models.CharField(max_length=100)
    year = models.DateField(blank=False, null=False)
    # more to be added