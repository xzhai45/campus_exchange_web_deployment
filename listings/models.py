from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from cloudinary.models import CloudinaryField

def validate_edu_email(value):
    """Custom validator to ensure the email ends with .edu"""
    if not value.lower().endswith('.edu'):
        raise ValidationError("Email must be from an .edu domain (e.g., user@university.edu)")
    
class Category(models.TextChoices):
    ELECTRONICS = "Electronics", "Electronics"
    BOOKS = "Books", "Books"
    CLOTHING = "Clothing", "Clothing"
    FURNITURE = "Furniture", "Furniture"
    APPLIANCES = "Appliances", "Appliances"
    AUTOMOBILES = "Automobiles", "Automobiles"
    OTHERS = "Others", "Others"

class Listing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # ✅ Ensure listing is linked to a user
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHERS)
    condition = models.CharField(max_length=50, choices=[
        ('New', 'New'),
        ('Like New', 'Like New'),
        ('Used', 'Used'),
        ('Fair', 'Fair'),
    ])
    seller = models.CharField(max_length=255)
    seller_contact = models.EmailField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    available = models.BooleanField(default=True)
    listing_date = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    tags = models.TextField(blank=True, null=True, help_text="Enter hashtags separated by spaces, e.g. #cat, #playstation")

    def __str__(self):
        return self.name
    

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image')

    def __str__(self):
        return f"Image for {self.listing.name}"
    


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    listings = models.ForeignKey(Listing,on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.listings.name