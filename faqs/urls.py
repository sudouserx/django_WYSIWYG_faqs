from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FAQViewSet

# Create a router and register the FAQViewSet
router = DefaultRouter()
router.register(r"faqs", FAQViewSet, basename="faq")

# Define the URL patterns
urlpatterns = [
    path("", include(router.urls)),  # Include the router's URLs
]
