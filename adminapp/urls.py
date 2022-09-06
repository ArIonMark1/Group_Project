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
from .views import *

urlpatterns = [
    path('', main, name='main'),
    path('contact/', edit_contacts, name='contact'),
    #категории
    path('question-category/', question_category, name='question_category'),
    path('question-category/edit/<int:pk>/', category, name='category_edit'),
    path('question-category/add/', add_category, name='category_add'),
    path('question-category/delete/<int:pk>/', delete_category, name='category_delete'),
    #вопросы
    path('questions/<int:pk>/', questions, name='questions'),
    path('questions/<int:pk_cat>/edit/<int:pk>/', question_edit, name='questions_edit'),
    path('questions/add/<int:pk_cat>', question_add, name='question_add'),
    path('questions/<int:pk_cat>/delete/<int:pk>/', question_delete, name='question_delete'),
    #сообщения от пользователей
    path('message/', message, name='message'),
    path('message-get/<int:pk>/', get_message, name='message_get'),
    path('message-delete/<int:pk>/', delete_message, name='message_delete'),
    #объявления
    path('offers/', offers, name='offers'),
    path('offers-pre-moderation/', pre_moderation, name='pre_moderation'),
    path('offers-pre-moderation/<int:pk>', show_offers_details, name='pre_moderation_details'),
    path('offers-pre-moderation/active/<int:pk>', allow_publishing, name='allow_publishing'),
    path('offers-convenience-type/', convenience_type, name='convenience_type'),
    path('offers-convenience-type-add/', convenience_type_add, name='convenience_type_add'),
    path('offers-convenience-type-delete/<int:pk>', convenience_type_delete, name='convenience_type_delete'),
    path('offers-convenience-type-edit/<int:pk>', convenience_type_edit, name='convenience_type_edit'),
    path('offers-convenience/<int:pk>', convenience, name='convenience'),
    path('offers-convenience/add/<int:pk_conv>', convenience_add, name='convenience_add'),
    path('offers-convenience-edit/<int:pk_conv>/<int:pk>/', convenience_edit, name='convenience_edit'),
    path('offers-convenience-delete/<int:pk_conv>/<int:pk>/', convenience_delete, name='convenience_delete'),
    path('user-booking/', booking, name='booking'),
    # категории объявлений
    path('room-category/', room_category, name='room_category'),
    path('room-category-edit/<int:pk>', room_category_edit, name='room_category_edit'),
    path('room-category-add/', room_category_add, name='room_category_add'),
    path('room-category-delete/<int:pk>', room_category_delete, name='room_category_delete'),
    #пользователи
    path('users/', users, name='users'),
    path('users/active/<int:pk>', staff_edit, name='staff_edit'),
    path('user/<int:pk>/', user, name='user'),
    #арендодатели
    path('landlords/', landlords, name='landlords'),
    path('landlords-history/', landlords_history, name='landlords_history'),
    path('landlord-history/<int:pk>/', landlord_history, name='landlord_history'),
    path('landlord/<int:pk>', landlord, name='landlord'),
    path('landlord/claim_accept/<int:pk>', claim_accept, name='claim_accept'),
    path('landlord/claim_reject/<int:pk>', claim_reject, name='claim_reject'),
    # отзывы
    path('criterion/', criterion, name='criterion'),
    path('criterion/add/', criterion_add, name='criterion_add'),
    path('criterion/edit/<int:pk>', criterion_edit, name='criterion_edit'),
    path('criterion/delete/<int:pk>', criterion_delete, name='criterion_delete'),
]
