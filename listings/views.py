
from django.shortcuts import render, get_object_or_404, redirect
from .models import Listing, Review
from django.db.models import Q 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Listing, ListingImage, Review
from .forms import ListingForm, ListingImageForm, ReviewForm
from django.http import JsonResponse
from .models import Listing
from django.conf import settings
from math import radians, cos, sin, sqrt, atan2
from django.core.paginator import Paginator

# Haversine Formula for Distance Calculation
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 3959  # Radius of the Earth in miles
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

def listings_api(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    max_distance = request.GET.get("distance", "no_limit")

    listings = Listing.objects.all().values("name", "price", "location", "latitude", "longitude", "id")

    if lat and lon and max_distance != "no_limit":
        lat, lon = float(lat), float(lon)
        max_distance = float(max_distance)

        # Filter listings within the selected radius
        listings = [listing for listing in listings if listing["latitude"] and listing["longitude"] and 
                    calculate_distance(lat, lon, listing["latitude"], listing["longitude"]) <= max_distance]

    return JsonResponse(list(listings), safe=False)
# Listings Page View
def index(request):
    search_query = request.GET.get('search', '').strip()
    listings = Listing.objects.all().order_by('-listing_date')

    if search_query:
        listings = listings.filter(
            Q(name__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # 12 listings per page
    paginator = Paginator(listings, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Listings',
        'listings': page_obj,  # pass page object instead of full queryset
        'search_query': search_query,
        'is_my_listings': False
    }
    return render(request, 'listings/index.html', context)



def show(request, id):
    # Find the listing with the matching ID
    listing = get_object_or_404(Listing, id=id)
    reviews = Review.objects.filter(listings=listing).order_by('-date')
    listing.views += 1
    listing.save(update_fields=['views'])

    context = {
        'title': listing.name,
        'listing': listing,
        'reviews': reviews
    }
    return render(request, 'listings/show.html', context)

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        listing = Listing.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.listings = listing
        review.user = request.user
        review.save()

        messages.success(request, "Your review has been successfully added!")

        return redirect('listings.show', id=id)
    else:
        return redirect('listings.show', id=id)


@login_required
def create_listing(request):
    if request.method == 'POST':
        listing_form = ListingForm(request.POST, request.FILES)

        if listing_form.is_valid():
            try:
                listing = listing_form.save(commit=False)
                listing.user = request.user  # ✅ Assign the logged-in user
                listing.seller_contact = request.user.email  # ✅ Automatically set email
                listing.seller = request.user.email
                listing.latitude = listing_form.cleaned_data.get("latitude")
                listing.longitude = listing_form.cleaned_data.get("longitude")
                listing.save()

                # ✅ Handle multiple image uploads
                images = request.FILES.getlist('images')  # Get all uploaded images
                if images:
                    for image in images:
                        ListingImage.objects.create(listing=listing, image=image)
                else:
                    messages.warning(request, "No images uploaded, consider adding some.")

                messages.success(request, "Listing created successfully!")
                return redirect('listings.index')

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

        else:
            messages.error(request, "Invalid form data. Please correct the errors below.")

    else:
        listing_form = ListingForm()

    return render(request, 'listings/create_listing.html', {
            'listing_form': listing_form,
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY # Pass the API key to the template
        })


def set_location(request):
    return render(request, 'listings/set_location.html', {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    })


    
@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if listing.user != request.user:
        messages.error(request, "You are not authorized to edit this listing.")
        return redirect('listings.index')

    if request.method == 'POST':
        listing_form = ListingForm(request.POST, request.FILES, instance=listing)

        if listing_form.is_valid():
            listing_form.save()

            images = request.FILES.getlist('images')
            if images:
                for image in images:
                    ListingImage.objects.create(listing=listing, image=image)

            messages.success(request, "Listing updated successfully!")
            return redirect('my_listings')
        else:
            messages.error(request, "There was an error updating the listing.")
    else:
        listing_form = ListingForm(instance=listing)

    return render(request, 'listings/edit_listing.html', {
        'listing_form': listing_form,
        'listing': listing,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    })


@login_required
def my_listings(request):
    listings = Listing.objects.filter(user=request.user)
    return render(request, 'listings/my_listings.html', {'listings': listings, 'is_my_listings': True})

@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if request.method == 'POST':  # Delete on POST request only
        listing.delete()
        messages.success(request, "Listing deleted successfully!")
        return redirect('listings.index')

    return render(request, 'listings/delete_listing.html', {'listing': listing})


@login_required
def delete_listing_image(request, image_id):
    image = get_object_or_404(ListingImage, id=image_id)
    listing_id = image.listing.id  # Save listing ID before deleting
    image.delete()
    messages.success(request, "Image deleted successfully!")
    return redirect('edit_listing', listing_id=listing_id)


@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, listings_id=id, user=request.user)  # Ensures user can only delete their own review
    
    if request.method == "POST":  # Ensure delete only happens on POST request
        review.delete()
        messages.success(request, "Your review has been successfully deleted.")
        return redirect('listings.show', id=id)

    messages.error(request, "Something went wrong. Try again.")
    return redirect('listings.edit_review', id=id, review_id=review_id)


@login_required
def edit_review(request, id, review_id):
    listing = get_object_or_404(Listing, id=id)
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated successfully!")
            return redirect('listings.show', id=id)
        else:
            messages.error(request, "Error updating review. Please try again.")

    else:
        form = ReviewForm(instance=review)

    return render(request, "listings/edit_review.html", {"listing": listing, "form": form, "review": review})