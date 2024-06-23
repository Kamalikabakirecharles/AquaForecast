from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # This handles password hashing
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    temperature = models.FloatField()
    condition = models.CharField(max_length=100)
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    
    
class EDAVisualization(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    visualization_base64 = models.TextField()  # Assuming you store base64 encoded images as text

    def __str__(self):
        return f"EDA Visualization for {self.uploaded_file.file.name}"
    
class Location(models.Model):
    LOCATION_TYPES = [
        ('Water Quality Site', 'Water Quality Site'),
        ('Hydrology Station', 'Hydrology Station'),
        ('Groundwater Station', 'Groundwater Station'),
    ]
    
    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=255)
    location_type = models.CharField(max_length=255, choices=LOCATION_TYPES)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    srid = models.IntegerField()

    def __str__(self):
        return self.name

class LocationData(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField()
    value = models.FloatField()

    def __str__(self):
        return f"{self.location.name} - {self.timestamp} - {self.value}"
    