from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),  # Django admin
    path("api/", include("faqs.urls")),  # FAQ app's URLs
]
