from django.shortcuts import render, HttpResponse
from listings.models import Listing
from math import radians, cos, sin, sqrt, atan2
from django.http import JsonResponse

def listings_api(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    max_distance = request.GET.get("distance", "no_limit")

    listings = Listing.objects.all().values("id", "name", "price", "location", "latitude", "longitude")

    listing_data = []

    for listing in listings:
        listing_obj = Listing.objects.get(id=listing["id"])
        if listing_obj.images.exists():
            image_url = request.build_absolute_uri(listing_obj.images.first().image.url)
        else:
            image_url = request.build_absolute_uri("/static/img/default-placeholder.png")

        listing_data.append({
            "id": listing["id"],
            "name": listing["name"],
            "price": listing["price"],
            "location": listing["location"],
            "latitude": listing["latitude"],
            "longitude": listing["longitude"],
            "image": image_url  # ✅ Include Image URL
        })

    return JsonResponse(listing_data, safe=False)


# Haversine Formula for Distance Calculation
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 3959  # Radius of the Earth in miles
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


def base_context(request):
    return {
        'nav_items': [
            ('Home', 'home.index'),
            ('About', 'home.about'),
            ('Listings', 'listings.index'), 
            ('Contact', 'home.contact'),
        ]
    }

def index(request):
    user_lat = request.GET.get("lat")
    user_lon = request.GET.get("lon")
    max_distance = request.GET.get("distance", "no_limit")

    listings = Listing.objects.all().order_by('-listing_date')  # Fetch all listings initially

    markers = []  # Stores markers for map display

    if user_lat and user_lon and max_distance != "no_limit":
        user_lat, user_lon = float(user_lat), float(user_lon)
        max_distance = float(max_distance)

        # Filter listings within the selected radius
        filtered_listings = []
        for listing in listings:
            if listing.latitude is not None and listing.longitude is not None:
                distance = calculate_distance(user_lat, user_lon, listing.latitude, listing.longitude)
                if distance <= max_distance:
                    filtered_listings.append(listing)
                    markers.append({
                        "name": listing.name,
                        "latitude": listing.latitude,
                        "longitude": listing.longitude,
                        "price": listing.price,
                        "location": listing.location
                    })
        listings = filtered_listings

    context = {
        'title': 'Listings',
        'listings': listings,
        'markers': markers,  # Pass markers for map rendering
    }
    return render(request, 'home/index.html', context)


def about(request):
    return render(request, "home/about.html")


def contact(request):  
    return render(request, 'home/contact.html')