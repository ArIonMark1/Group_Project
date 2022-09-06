"""mainapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import user, user_profile, user_bookings, user_favorites, user_locations, claim_landlord
from .views import booking_history, users, change_ad


app_name = 'userapp'

urlpatterns = [
    path('', user, name='main'),
    path('profile/', user_profile, name='profile'),
    path('bookings/', user_bookings, name='bookings'),
    path('locations/', user_locations, name='locations'),
    path('favorites/', user_favorites, name='favorites'),
    path('landlord-application/', claim_landlord, name='landlord-application'),
    path('booking-history/', booking_history, name='booking_history'),
    path('users/<int:pk>', users, name='users'),
    path('change-ad/<int:pk>', change_ad, name='change_ad'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
