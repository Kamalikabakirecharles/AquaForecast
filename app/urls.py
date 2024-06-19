# app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('weather/', views.weather, name='weather'),
    path('historical_analysis/', views.historical_analysis, name='historical_analysis'),
    path('spatial_analysis/', views.spatial_analysis, name='spatial_analysis'),
    path('environmental_factors/', views.environmental_factors, name='environmental_factors'),
    path('save_weather_data/', views.save_weather_data, name='save_weather_data'),
    path('upload_dataset/', views.upload_dataset, name='upload_dataset'),
    path('download_image/<int:eda_visualizations_id>/', views.download_image, name='download_image'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('visualization/', views.visualization_page, name='visualization_page'),
    path('eda_historical/', views.eda_historical, name='eda_historical'),
]
