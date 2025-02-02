from unittest.mock import patch

import pytest
from django.db import IntegrityError
from googletrans.models import Translated

from faqs.models import FAQ, FAQTranslation


@pytest.mark.django_db
def test_faq_creation():
    faq = FAQ.objects.create(question="How to use?", answer="Step by step.")
    assert faq.question == "How to use?"
    assert faq.answer == "Step by step."


@pytest.mark.django_db
def test_get_translated_question_existing_translation():
    faq = FAQ.objects.create(question="Help?", answer="Here.")
    FAQTranslation.objects.create(faq=faq, language="hi", translated_text="मदद?")

    translated = faq.get_translated_question("hi")
    assert translated == "मदद?"


@pytest.mark.django_db
@patch("googletrans.Translator.translate")
def test_get_translated_question_auto_translate(mock_translate):
    mock_translate.return_value = Translated(
        text="Aide?", src="en", dest="fr", origin="Help?", pronunciation=None, parts=[]
    )
    faq = FAQ.objects.create(question="Help?", answer="Here.")

    # First call creates translation
    translated = faq.get_translated_question("fr")
    assert translated == "Aide?"

    # Verify translation was saved
    translation = FAQTranslation.objects.get(faq=faq, language="fr")
    assert translation.translated_text == "Aide?"


@pytest.mark.django_db
@patch("googletrans.Translator.translate")
def test_get_translated_question_translation_failure(mock_translate):
    mock_translate.side_effect = Exception("API Error")
    faq = FAQ.objects.create(question="Help?", answer="Here.")

    translated = faq.get_translated_question("fr")
    assert translated == "Help?"  # Fallback to original


@pytest.mark.django_db
def test_faq_translation_unique_constraint():
    faq = FAQ.objects.create(question="Hi?", answer="Hello.")
    FAQTranslation.objects.create(faq=faq, language="es", translated_text="¿Hola?")

    with pytest.raises(IntegrityError):
        FAQTranslation.objects.create(faq=faq, language="es", translated_text="¿Hola?")
