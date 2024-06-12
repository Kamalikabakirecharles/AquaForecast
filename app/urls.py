# app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('historical_analysis/', views.historical_analysis, name='historical_analysis'),
    path('spatial_analysis/', views.spatial_analysis, name='spatial_analysis'),
    path('environmental_factors/', views.environmental_factors, name='environmental_factors'),
    path('save_weather_data/', views.save_weather_data, name='save_weather_data'),
]
