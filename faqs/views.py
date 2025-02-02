from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.response import Response

from .models import FAQ
from .serializers import FAQSerializer

CACHE_TIMEOUT = 60 * 15  # 15 minutes
CACHE_VERSION_KEY = "faq_cache_version"


def get_cache_version():
    """
    Retrieve the current FAQ cache version.
    If it doesn't exist, initialize it to 1.
    """
    version = cache.get(CACHE_VERSION_KEY)
    if version is None:
        version = 1
        cache.set(CACHE_VERSION_KEY, version)
    return version


def increment_cache_version():
    """
    Increment the FAQ cache version.
    """
    version = get_cache_version()
    cache.set(CACHE_VERSION_KEY, version + 1)
    return version + 1


class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def get_list_cache_key(self, lang="en"):
        version = get_cache_version()
        return f"faqs_list_{lang}_v{version}"

    def get_detail_cache_key(self, pk, lang="en"):
        version = get_cache_version()
        return f"faq_detail_{pk}_{lang}_v{version}"

    def list(self, request, *args, **kwargs):
        lang = request.query_params.get("lang", "en")
        cache_key = self.get_list_cache_key(lang)
        data = cache.get(cache_key)
        if data is not None:
            return Response(data)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TIMEOUT)
        return response

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        lang = request.query_params.get("lang", "en")
        cache_key = self.get_detail_cache_key(pk, lang)
        data = cache.get(cache_key)
        if data is not None:
            return Response(data)
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TIMEOUT)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        increment_cache_version()  # Invalidate list/detail caches by bumping the version
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        increment_cache_version()  # Invalidate caches
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        increment_cache_version()  # Invalidate caches
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        increment_cache_version()  # Invalidate caches
        return response
