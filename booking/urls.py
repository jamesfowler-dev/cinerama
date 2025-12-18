from django.urls import path
from . import views

urlpatterns = [
    path("", views.booking_view, name='booking'),
    path('select-seats/<int:showtime_id>/', views.select_seats, name='select_seats'),
    path('proceed-to-login/', views.proceed_to_login, name='proceed_to_login'),
    path('review-booking/', views.review_booking, name='review_booking'),
    path('confirm/', views.confirm_booking, name='confirm_booking'),
    path('success/<uuid:booking_id>/', views.booking_success, name='booking_success'),
    path('confirm-reselect/<uuid:booking_id>/', views.confirm_reselect, name='confirm_reselect'),
    path('manage/', views.manage_bookings, name='manage_bookings'),
    path('edit/<uuid:booking_id>/', views.edit_booking, name='edit_booking'),
    path('delete/<uuid:booking_id>/', views.delete_booking, name='delete_booking'),
]
