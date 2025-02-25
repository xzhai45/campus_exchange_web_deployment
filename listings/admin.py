from django.contrib import admin
from .models import Listing, Review, ListingImage

# ✅ Inline model to allow multiple image uploads in the admin panel
class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 3  # Allows uploading up to 3 images at a time

# ✅ Register Listing with ListingImage Inline
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'condition', 'seller', 'available')
    search_fields = ('name', 'category', 'condition', 'seller')
    list_filter = ('category', 'condition', 'available')
    inlines = [ListingImageInline]  # ✅ Enables multiple image uploads inside Listing

# ✅ Register Review model
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    ordering = ('date',)  # Order by date
    search_fields = ['comment']
