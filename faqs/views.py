import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import FAQ
from .serializers import FAQSerializer
from .tasks import translate_faq_language

CACHE_TIMEOUT = 60 * 15  # 15 minutes
CACHE_VERSION_KEY = "faq_cache_version"

logger = logging.getLogger(__name__)


# Cache utilities
def get_cache_version():
    version = cache.get(CACHE_VERSION_KEY)
    return version or 1


def increment_cache_version():
    version = get_cache_version() + 1
    cache.set(CACHE_VERSION_KEY, version)
    return version


def get_cache_key(resource_type, identifier, lang):
    version = get_cache_version()
    return f"faq_{resource_type}_{identifier}_{lang}_v{version}"


class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def _get_cached_or_fetch(self, cache_key, fetch_fn):
        if cached := cache.get(cache_key):
            return Response(cached)
        response = fetch_fn()
        cache.set(cache_key, response.data, CACHE_TIMEOUT)
        return response

    def list(self, request, *args, **kwargs):
        lang = request.query_params.get("lang", "en")
        logger.debug(f"Starting FAQ list request for {lang}")
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"List request failed for {lang}: {str(e)}", exc_info=True)
            raise

    def retrieve(self, request, *args, **kwargs):
        lang = request.query_params.get("lang", "en")
        cache_key = get_cache_key("detail", kwargs["pk"], lang)

        if cached := cache.get(cache_key):
            return Response(cached)

        # Call the parent class's retrieve method directly
        response = super(FAQViewSet, self).retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TIMEOUT)
        return response

    def _trigger_translations(self, faq_id):
        for lang in settings.POPULAR_INDIAN_LANGUAGES:
            translate_faq_language.delay_on_commit(faq_id, lang)

    def _handle_update(self, request, partial):
        instance = self.get_object()
        old_question = instance.question
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if old_question != serializer.instance.question:
            self._trigger_translations(serializer.instance.id)

        increment_cache_version()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self._trigger_translations(serializer.instance.id)
        increment_cache_version()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        return self._handle_update(request, partial=False)

    def partial_update(self, request, *args, **kwargs):
        return self._handle_update(request, partial=True)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        increment_cache_version()
        return Response(status=status.HTTP_204_NO_CONTENT)
