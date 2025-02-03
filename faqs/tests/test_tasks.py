import logging
from unittest.mock import MagicMock, patch

import pytest
from celery.exceptions import Retry
from django.core.exceptions import ObjectDoesNotExist

from faqs.models import FAQ, FAQTranslation
from faqs.tasks import translate_faq_language

logger = logging.getLogger(__name__)


@pytest.fixture
def faq():
    return FAQ.objects.create(
        question="What is your return policy?", answer="30 days return policy"
    )


@pytest.fixture
def existing_translation(faq):
    return FAQTranslation.objects.create(
        faq=faq, language="es", translated_text="¿Cuál es su política de devolución?"
    )


@pytest.mark.django_db
class TestTranslateFaqLanguage:
    def test_successful_translation(self, faq, mocker):
        # Patch the Translator imported in tasks.py
        mock_translator = mocker.patch("faqs.tasks.Translator")
        mock_translator.return_value.translate.return_value = MagicMock(
            text="Quelle est votre politique de retour?"
        )

        # Execute
        translate_faq_language(faq.id, "fr")

        # Verify
        translation = FAQTranslation.objects.get(faq=faq, language="fr")
        assert translation.translated_text == "Quelle est votre politique de retour?"
        mock_translator.return_value.translate.assert_called_once_with(
            "What is your return policy?", dest="fr"
        )

    def test_existing_translation(self, existing_translation, mocker):
        # Patch the Translator imported in tasks.py
        mock_translator = mocker.patch("faqs.tasks.Translator")

        # Execute
        translate_faq_language(existing_translation.faq.id, "es")

        # Verify
        mock_translator.return_value.translate.assert_not_called()

    def test_nonexistent_faq(self, caplog):
        # Execute
        with pytest.raises(ObjectDoesNotExist):
            translate_faq_language(9999, "de")

        # Verify
        assert "FAQ 9999 does not exist" in caplog.text

    def test_translation_retry(self, faq, mocker):
        # Setup
        mock_retry = mocker.patch.object(translate_faq_language, "retry")
        mock_retry.side_effect = Retry()
        # Patch the Translator imported in tasks.py
        mocker.patch("faqs.tasks.Translator").side_effect = Exception("API Error")

        # Execute & Verify
        with pytest.raises(Retry):
            translate_faq_language(faq.id, "it")

        assert mock_retry.call_count == 1

    def test_general_exception_handling(self, faq, mocker, caplog):
        # Patch the Translator imported in tasks.py
        mocker.patch("faqs.tasks.Translator").side_effect = Exception(
            "Unexpected error"
        )

        # Execute
        with pytest.raises(Exception):
            translate_faq_language(faq.id, "ja")

        # Verify
        assert "Translation task failed" in caplog.text
        assert "Unexpected error" in caplog.text

    # def test_translation_flow_with_retries(self, faq, mocker):
    #     # Patch the Translator imported in tasks.py
    #     mock_translator = mocker.patch('faqs.tasks.Translator')
    #     mock_translator.return_value.translate.side_effect = [
    #         Exception("Temporary error"),
    #         MagicMock(text="Qual é a sua política de retorno?")
    #     ]

    #     # Execute
    #     try:
    #         translate_faq_language(faq.id, "pt")
    #     except Retry:
    #         translate_faq_language(faq.id, "pt")

    #     # Verify
    #     translation = FAQTranslation.objects.get(faq=faq, language="pt")
    #     assert translation.translated_text == "Qual é a sua política de retorno?"
    #     assert mock_translator.return_value.translate.call_count == 2
