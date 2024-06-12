from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login
import requests
from app.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.conf import settings
from .models import WeatherData  

# Create your views here.
def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def historical_analysis(request):
    return render(request, 'historical_analysis.html')

def spatial_analysis(request):
    return render(request, 'spatial_analysis.html')

def environmental_factors(request):
    return render(request, 'environmental_factors.html')


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        # Create and save the user with a hashed password
        user = User.objects.create(email=email, phone_number=phone_number, password=make_password(password))
        user.save()
        
        # Redirect to login page after successful signup
        return redirect('login')
    
    return render(request, 'signup.html')

def login(request):
    # If the user is already authenticated, redirect to the dashboard
    if request.user.is_authenticated:
        print("User is already authenticated")
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')  # Use email as username
        password = request.POST.get('password')

        print("Email:", email)  # Print email for debugging
        print("Password:", password)  # Print password for debugging

        user = authenticate(request, email=email, password=password)  # Authenticate using email and password
        if user is not None:
            auth_login(request, user)
            print("User authenticated successfully")
            return redirect('dashboard')  # Redirect to dashboard upon successful login
        else:
            # Display error message if authentication fails
            error_message = "Invalid credentials. Please try again."
            messages.error(request, error_message)
            print("Authentication failed")

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def get_weather_data():
    api_key = settings.OPENWEATHERMAP_API_KEY
    city = "kigali"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

def environmental_factors(request):
    weather_data = get_weather_data()
    weather_code = weather_data.get('weather', [{}])[0].get('id', 800)  # Default to Clear if weather code is not available
    category, image = map_weather_conditions(weather_code)
    
    # Pass weather data as initial values to the form
    initial_data = {
        'city': weather_data.get('name', ''),
        'temperature': weather_data.get('main', {}).get('temp', ''),
        'condition': category,
        'humidity': weather_data.get('main', {}).get('humidity', ''),
        'wind_speed': weather_data.get('wind', {}).get('speed', ''),
    }
    
    context = {
        'weather': weather_data,
        'weather_category': category,
        'weather_image': image,
        'initial_data': initial_data  # Pass initial data to the template
    }
    return render(request, 'environmental_factors.html', context)


def map_weather_conditions(weather_code):
    if 200 <= weather_code <= 232:  # Thunderstorm
        return "Thunderstorm", "thunderstorm.png"
    elif 300 <= weather_code <= 321:  # Drizzle
        return "Drizzle", "drizzle.png"
    elif 500 <= weather_code <= 531:  # Rain
        return "Rain", "rain.png"
    elif 600 <= weather_code <= 622:  # Snow
        return "Snow", "snow.png"
    elif 701 <= weather_code <= 781:  # Atmosphere
        return "Atmosphere", "atmosphere.png"
    elif weather_code == 800:  # Clear
        return "Clear", "clear.png"
    elif 801 <= weather_code <= 804:  # Clouds
        return "Clouds", "clouds.png"
    else:
        return "Unknown", "default.png"  # Handle unknown conditions
    
def save_weather_data(request):
    if request.method == 'POST':
        # Extract weather data from the request
        city = request.POST.get('city')
        temperature = request.POST.get('temperature')
        condition = request.POST.get('condition')
        humidity = request.POST.get('humidity')
        wind_speed = request.POST.get('wind_speed')
        
        try:
            # Save the weather data to the database
            WeatherData.objects.create(
                city=city,
                temperature=temperature,
                condition=condition,
                humidity=humidity,
                wind_speed=wind_speed
            )
            return JsonResponse({'success': True, 'message': 'Weather data saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return HttpResponseBadRequest("Invalid request method")