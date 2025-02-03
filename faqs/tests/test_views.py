from unittest.mock import patch

import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIRequestFactory

from faqs.models import FAQ, FAQTranslation
from faqs.views import (
    FAQViewSet,
    get_cache_key,
    get_cache_version,
    increment_cache_version,
)


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def faq():
    return FAQ.objects.create(question="Test?", answer="Answer.")


@pytest.mark.django_db
class TestFAQViewSet:
    def test_retrieve_view_cache(self, api_rf, faq):
        view = FAQViewSet.as_view({"get": "retrieve"})
        request = api_rf.get(f"/faqs/{faq.pk}/", {"lang": "en"})

        # First request should populate cache
        response = view(request, pk=faq.pk)
        assert response.status_code == status.HTTP_200_OK

        # Get the actual cache key used
        cache_key = get_cache_key("detail", faq.pk, "en")
        cached_data = cache.get(cache_key)
        assert cached_data == response.data

        # Second request with controlled cache mock
        original_cache_get = cache.get  # Preserve original cache.get

        def mock_cache_get(key, default=None):
            """Only mock requests for the FAQ cache key"""
            if key == cache_key:
                return cached_data
            return original_cache_get(key, default)

        with patch.object(cache, "get", side_effect=mock_cache_get) as mock_get:
            cached_response = view(request, pk=faq.pk)

            # Verify the mock was called with the correct key
            mock_get.assert_any_call(cache_key)
            assert cached_response.data == response.data

    def test_cache_version_increment(self):
        initial_version = get_cache_version()
        increment_cache_version()
        assert get_cache_version() == initial_version + 1

    def test_create_invalidates_cache(self, api_rf):
        initial_version = get_cache_version()
        view = FAQViewSet.as_view({"post": "create"})
        data = {"question": "New?", "answer": "New answer."}
        request = api_rf.post("/faqs/", data, format="json")

        response = view(request)
        assert response.status_code == status.HTTP_201_CREATED
        assert get_cache_version() == initial_version + 1

    def test_retrieve_view_translation(self, api_rf, faq):
        view = FAQViewSet.as_view({"get": "retrieve"})
        request = api_rf.get(f"/faqs/{faq.pk}/", {"lang": "hi"})

        with patch.object(FAQ, "get_translated_question") as mock_translate:
            mock_translate.return_value = "परीक्षा?"
            response = view(request, pk=faq.pk)

            assert response.data["question"] == "परीक्षा?"
            mock_translate.assert_called_with("hi")

    def test_cache_key_generation(self):
        pk = 123
        lang = "bn"
        cache_key = get_cache_key("detail", pk, lang)
        assert f"faq_detail_{pk}_{lang}_v" in cache_key
        assert str(get_cache_version()) in cache_key

    def test_update_invalidates_cache(self, api_rf, faq):
        initial_version = get_cache_version()
        view = FAQViewSet.as_view({"patch": "partial_update"})
        data = {"question": "Updated?"}
        request = api_rf.patch(f"/faqs/{faq.pk}/", data, format="json")

        response = view(request, pk=faq.pk)
        assert response.status_code == status.HTTP_200_OK
        assert get_cache_version() == initial_version + 1

    def test_delete_invalidates_cache(self, api_rf, faq):
        initial_version = get_cache_version()
        view = FAQViewSet.as_view({"delete": "destroy"})
        request = api_rf.delete(f"/faqs/{faq.pk}/")

        response = view(request, pk=faq.pk)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert get_cache_version() == initial_version + 1

    def test_translation_fallback_mechanism(self, api_rf, faq):
        # Create empty translation
        FAQTranslation.objects.create(faq=faq, language="hi", translated_text="")

        view = FAQViewSet.as_view({"get": "retrieve"})
        request = api_rf.get(f"/faqs/{faq.pk}/", {"lang": "hi"})

        with patch("faqs.models.Translator") as mock_translator:
            mock_translator.return_value.translate.side_effect = Exception("API error")
            response = view(request, pk=faq.pk)

        assert response.data["question"] == faq.question  # Fallback to English
        assert FAQTranslation.objects.get(faq=faq, language="hi").translated_text == ""

    def test_cache_version_consistency(self):
        cache.clear()
        version1 = get_cache_version()
        increment_cache_version()
        version2 = get_cache_version()
        assert version2 == version1 + 1
        assert cache.get("faq_cache_version") == version2
