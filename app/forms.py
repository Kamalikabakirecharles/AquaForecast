# forms.py
from django import forms
from .models import Location, LocationData

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'identifier', 'location_type', 'longitude', 'latitude', 'srid']

class LocationDataForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = LocationData
        fields = ['location', 'timestamp', 'value']