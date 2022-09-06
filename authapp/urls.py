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
from authapp.views import login, user_logout, UserRegisterView, choose_type, landlord_register, verify

app_name = 'authapp'

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('choose/', choose_type, name='choose_type'),
    path('user/', UserRegisterView.as_view(), name='user'),
    path('landlord/', landlord_register, name='landlord'),
    path('verify/<email>/<activation_key>/', verify, name='verify'),
]
