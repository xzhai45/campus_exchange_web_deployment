import requests
from django import forms
from .models import Listing, ListingImage, Review, Category
from django.conf import settings

class ListingForm(forms.ModelForm):

    images = forms.FileField(required=False)
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Listing
        exclude = ['user']
        fields = ['name', 'price', 'description', 'category', 'condition', 'seller', 'seller_contact', 'location', 'available', 'tags', 'latitude', 'longitude']

        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),  # ✅ Ensure price is a number field
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control'}),
            'category': forms.Select(choices=Category.choices, attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tags': forms.TextInput(attrs={'placeholder': 'e.g., #gaming #furniture', 'class': 'form-control'}),
        }

    def clean_location(self):
        location = self.cleaned_data.get("location")

        if location:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": location,
                "key": settings.GOOGLE_MAPS_API_KEY  # Store the API key in settings.py
            }
            response = requests.get(url, params=params)

            if response.status_code == 200:
                geo_data = response.json()
                if geo_data["status"] == "OK":
                    coordinates = geo_data["results"][0]["geometry"]["location"]
                    self.cleaned_data["latitude"] = coordinates["lat"]
                    self.cleaned_data["longitude"] = coordinates["lng"]
                else:
                    raise forms.ValidationError("Could not determine coordinates for this location.")
            else:
                raise forms.ValidationError("Failed to fetch location data.")

        return location    

class ListingImageForm(forms.ModelForm):
    image = forms.ImageField()  # Allows multiple file selection
    
    class Meta:
        model = ListingImage
        fields = ['image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']
