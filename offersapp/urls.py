from django.conf import settings
from django.conf.urls.static import static
# from django.contrib import admin
from django.urls import path

from offersapp.views import main, SearchResultsView

urlpatterns = [
    path('', main, name='main'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
