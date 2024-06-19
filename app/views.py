import base64
from collections import defaultdict
import json
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login
import pandas as pd
import requests
from app.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.conf import settings
from .models import WeatherData
from django.views.decorators.csrf import csrf_exempt
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import os
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from .models import UploadedFile, EDAVisualization
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image
from django.shortcuts import get_object_or_404




# Create your views here.
def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard_design.html')

@login_required
def historical_analysis(request):
    return render(request, 'historical_analysis.html')

@login_required
def spatial_analysis(request):
    return render(request, 'spatial_analysis.html')

@login_required
def environmental_factors(request):
    return render(request, 'environmental_factors.html')

@login_required
def weather(request):
    return render(request, 'weather.html')

@login_required
def upload_dataset(request):
    return render(request, 'upload_dataset.html')

@login_required
def visualization(request):
    return render(request, 'visualization.html')


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

def get_weather_data(city):
    api_key = settings.OPENWEATHERMAP_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()


def weather(request):
    cities = [
        "Kigali", "Butare", "Gisenyi", "Rwamagana",
        "Kibuye", "Byumba", "Cyangugu", "Ruhengeri",
        "Nyanza", "Kibungo"
    ]
    
    weather_data_list = []
    
    for city in cities:
        weather_data = get_weather_data(city)
        weather_code = weather_data.get('weather', [{}])[0].get('id', 800)  # Default to Clear if weather code is not available
        category, image = map_weather_conditions(weather_code)
        
        weather_data_list.append({
            'city': city,
            'temperature': weather_data.get('main', {}).get('temp', ''),
            'condition': category,
            'humidity': weather_data.get('main', {}).get('humidity', ''),
            'wind_speed': weather_data.get('wind', {}).get('speed', ''),
            'weather_category': category,
            'weather_image': image,
        })
    
    context = {
        'weather_data_list': weather_data_list
    }
    
    return render(request, 'weather.html', context)



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
    
@csrf_exempt
def save_weather_data(request):
    if request.method == 'POST':
        cities = request.POST.getlist('cities[]')
        temperatures = request.POST.getlist('temperatures[]')
        conditions = request.POST.getlist('conditions[]')
        humidities = request.POST.getlist('humidities[]')
        wind_speeds = request.POST.getlist('wind_speeds[]')

        try:
            for i in range(len(cities)):
                WeatherData.objects.create(
                    city=cities[i],
                    temperature=temperatures[i],
                    condition=conditions[i],
                    humidity=humidities[i],
                    wind_speed=wind_speeds[i]
                )
            return JsonResponse({'success': True, 'message': 'Weather data saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return HttpResponseBadRequest("Invalid request method")



# Function to perform EDA and return base64 encoded images
def perform_eda(df):
    visualizations = []

    # Example EDA: Count plot of weather types
    plt.figure(figsize=(10, 6))
    sns.countplot(x='weather', data=df)
    plt.title('Distribution of Weather Types')
    plt.xlabel('Weather')
    plt.ylabel('Count')
    
    # Save plot to a BytesIO object and encode as base64
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    visualization_base64 = base64.b64encode(img.getvalue()).decode()
    visualizations.append({'title': 'Distribution of Weather Types', 'image': visualization_base64})
    plt.close()

    # Box plots for numerical variables vs weather
    plt.figure(figsize=(14, 8))

    plt.subplot(2, 2, 1)
    sns.boxplot(x='weather', y='precipitation', data=df)
    plt.title('Precipitation vs Weather')

    plt.subplot(2, 2, 2)
    sns.boxplot(x='weather', y='temp_max', data=df)
    plt.title('Max Temperature vs Weather')

    plt.subplot(2, 2, 3)
    sns.boxplot(x='weather', y='temp_min', data=df)
    plt.title('Min Temperature vs Weather')

    plt.subplot(2, 2, 4)
    sns.boxplot(x='weather', y='wind', data=df)
    plt.title('Wind vs Weather')

    plt.tight_layout()

    # Save the boxplot figure
    img_boxplot = BytesIO()
    plt.savefig(img_boxplot, format='png')
    img_boxplot.seek(0)
    visualization_boxplot_base64 = base64.b64encode(img_boxplot.getvalue()).decode()
    visualizations.append({'title': 'Boxplots for Weather Variables', 'image': visualization_boxplot_base64})
    plt.close()

    # Pairplot to show relationships between numerical features
    plt.figure(figsize=(12, 8))
    sns.pairplot(df, hue='weather')
    plt.title('Pairplot of Numerical Features with Weather')
    
    # Save the pairplot figure
    img_pairplot = BytesIO()
    plt.savefig(img_pairplot, format='png')
    img_pairplot.seek(0)
    visualization_pairplot_base64 = base64.b64encode(img_pairplot.getvalue()).decode()
    visualizations.append({'title': 'Pairplot of Numerical Features', 'image': visualization_pairplot_base64})
    plt.close()

    return visualizations




@csrf_exempt
def upload_dataset(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # Save the uploaded file to the database
        uploaded_instance = UploadedFile(file=uploaded_file)
        uploaded_instance.save()

        try:
            # Read the uploaded CSV file into a Pandas DataFrame
            df = pd.read_csv(uploaded_file)

            # Perform exploratory data analysis (EDA)
            visualizations = perform_eda(df)

            # Get all saved files from the database (updated list)
            saved_files = UploadedFile.objects.all()

            context = {
                'saved_files': saved_files,
                'visualizations': visualizations,
            }

            return render(request, 'environmental_factors.html', context)

        except pd.errors.EmptyDataError:
            return HttpResponseBadRequest("Uploaded file is empty or invalid")

    elif request.method == 'POST':
        return JsonResponse({'success': False, 'message': 'No file received in request'})

    # Fetch all saved files for the initial rendering of the page
    saved_files = UploadedFile.objects.all()

    # Render the environmental_factors.html template for GET requests or if no file uploaded
    context = {
        'saved_files': saved_files,
        'visualizations': None,  # or initialize as needed
    }
    return render(request, 'upload_dataset.html', context)

@csrf_exempt
def environmental_factors(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        try:
            uploaded_file = UploadedFile.objects.get(id=file_id)
            df = pd.read_csv(uploaded_file.file)

            # Perform EDA and get visualizations
            visualizations = perform_eda(df)

            # Save individual visualizations to database (optional)
            for vis in visualizations:
                EDAVisualization.objects.create(
                    uploaded_file=uploaded_file,
                    visualization_base64=vis['image']
                )

            return JsonResponse({'success': True, 'visualizations': visualizations})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    # Fetch all saved files for the initial rendering of the page
    saved_files = UploadedFile.objects.all()

    context = {
        'saved_files': saved_files,
    }
    return render(request, 'environmental_factors.html', context)



@login_required
def eda_historical(request):
    # Fetch all saved EDA visualizations
    eda_visualizations = EDAVisualization.objects.all()
    context = {
        'eda_visualizations': eda_visualizations,
    }
    return render(request, 'eda_historical.html', context)


def download_image(request, eda_visualizations_id):
    eda_visualizations = get_object_or_404(EDAVisualization, id=eda_visualizations_id)
    
    # Decode the base64 image
    image_data = base64.b64decode(eda_visualizations.visualization_base64)
    
    # Serve the image directly as a response
    response = HttpResponse(image_data, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename={eda_visualizations.uploaded_file.file.name}.png'
    return response

@login_required
def generate_pdf(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        try:
            uploaded_file = UploadedFile.objects.get(id=file_id)
            eda_visualizations = EDAVisualization.objects.filter(uploaded_file=uploaded_file)[:3]  # Limit to 3 images

            # Create a BytesIO buffer to store PDF
            buffer = BytesIO()

            # Create PDF document
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1 * inch, 10.5 * inch, "Environmental Data Analysis Report")
            c.setFont("Helvetica", 12)

            y_position = 10 * inch  # Start position for content

            first_image = True  # Flag to adjust first image positioning

            for i, vis in enumerate(eda_visualizations):
                # Decode base64 image
                image_data = base64.b64decode(vis.visualization_base64)
                image_stream = BytesIO(image_data)
                image = Image.open(image_stream)

                # Calculate image dimensions for scaling
                image_width, image_height = image.size
                aspect_ratio = image_width / float(image_height)
                desired_width = 5.5 * inch  # Adjust based on your layout preference
                image_height = desired_width / aspect_ratio

                # Check if there's enough space for the next image; otherwise, create a new page
                if not first_image and y_position - image_height < 1 * inch:
                    c.showPage()
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(1 * inch, 10.5 * inch, "Environmental Data Analysis Report")
                    c.setFont("Helvetica", 12)
                    y_position = 10 * inch  # Reset y_position for new page

                # Adjust y_position for first image to avoid cut-off
                if not first_image:
                    y_position -= 1.5 * inch  # Add space between images
                else:
                    first_image = False

                # Add image to PDF
                c.drawString(1 * inch, y_position - 0.2 * inch, f"EDA Visualization: {uploaded_file.file.name}")
                c.drawInlineImage(image, 1 * inch, y_position - 1 * inch - image_height, width=desired_width, height=image_height)

                # Update y_position for the next image
                y_position -= image_height

            c.save()

            buffer.seek(0)

            # Prepare response to download PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="EDA_Report.pdf"'
            response.write(buffer.getvalue())

            return response

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return HttpResponseBadRequest("Invalid request method")

logger = logging.getLogger(__name__)

@login_required
def visualization_page(request):
    city_name = request.GET.get('city')

    # Fetch weather data for the specified city
    logger.info(f"Fetching weather data for city: {city_name}")
    weather_data = WeatherData.objects.filter(city=city_name).order_by('timestamp')

    if not weather_data.exists():
        logger.warning("No weather data found")
        return render(request, 'visualization.html', {'city_name': city_name, 'error': "No weather data found for the specified city."})

    logger.info("Weather data retrieved successfully")
    data = pd.DataFrame(list(weather_data.values()))
    logger.debug(f"Data fetched: {data.head()}")

    visualizations = generate_visualizations(data)
    logger.debug(f"Generated visualizations: {visualizations}")

    return render(request, 'visualization.html', {
        'city_name': city_name,
        'visualizations': json.dumps(visualizations)  # Serialize the visualizations to JSON
    })

def generate_visualizations(data):
    visualizations = {
        'temperature': {
            'timestamps': data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'values': data['temperature'].tolist()
        },
        'humidity': {
            'timestamps': data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'values': data['humidity'].tolist()
        },
        'wind_speed': {
            'timestamps': data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'values': data['wind_speed'].tolist()
        }
    }
    return visualizations