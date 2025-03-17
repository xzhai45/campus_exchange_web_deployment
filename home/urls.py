from django.urls import path
from . import views
from .views import listings_api

urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    path('contact', views.contact, name='home.contact'),
    path('api/listings/', listings_api, name='listings_api'),
    
]
