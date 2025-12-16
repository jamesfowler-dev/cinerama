from django.urls import path
from . import views

urlpatterns = [
    path("", views.booking_view, name='booking'),
    path('select-seats/<int:showtime_id>/', views.select_seats, name='select_seats'),
    path('proceed-to-login/', views.proceed_to_login, name='proceed_to_login'),
    path('review-booking/', views.review_booking, name='review_booking'),
    path('confirm/', views.confirm_booking, name='confirm_booking'),
    path('success/<uuid:booking_id>/', views.booking_success, name='booking_success'),
]
