from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='listings.index'),
    path('<int:id>/', views.show, name='listings.show'),
    path("<int:id>/reviews/create/", views.create_review, name="listings.create_review"),
    path('<int:id>/review/<int:review_id>/edit/',views.edit_review, name='listings.edit_review'),
    path("<int:id>/reviews/<int:review_id>/delete/", views.delete_review, name="listings.delete_review"),
    path('create/', views.create_listing, name='listings.create_listing'),
    path('listing/edit/<int:listing_id>/', views.edit_listing, name='edit_listing'),
    path('listing/delete/<int:listing_id>/', views.delete_listing, name='delete_listing'),
    path('listing/image/delete/<int:image_id>/', views.delete_listing_image, name='delete_listing_image'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('', views.index, name='listings.index'),
    path('api/listings/', views.listings_api, name='listings_api'),


]