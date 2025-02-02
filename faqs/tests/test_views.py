from unittest.mock import patch

import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIRequestFactory

from faqs.models import FAQ
from faqs.views import FAQViewSet, get_cache_version, increment_cache_version


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def faq():
    return FAQ.objects.create(question="Test?", answer="Answer.")


@pytest.mark.django_db
class TestFAQViewSet:
    def test_list_view_cache(self, api_rf, faq):
        view = FAQViewSet.as_view({"get": "list"})
        request = api_rf.get("/faqs/", {"lang": "en"})

        response = view(request)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        cache_key = FAQViewSet().get_list_cache_key(lang="en")
        cached_data = cache.get(cache_key)
        assert cached_data == response.data

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
        request = api_rf.get("/faqs/1/", {"lang": "hi"})

        with patch.object(FAQ, "get_translated_question") as mock_translate:
            mock_translate.return_value = "परीक्षा?"
            response = view(request, pk=faq.pk)

            assert response.data["question"] == "परीक्षा?"
            mock_translate.assert_called_with("hi")

    def test_cache_key_includes_language_and_version(self, api_rf):
        request = api_rf.get("/faqs/", {"lang": "bn"})
        cache_key = FAQViewSet().get_list_cache_key(request)
        assert "bn" in cache_key
        assert f"v{get_cache_version()}" in cache_key
