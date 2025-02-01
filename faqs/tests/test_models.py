from unittest.mock import patch

from django.test import TestCase

from .models import FAQ


class FAQModelTest(TestCase):
    @patch("googletrans.Translator.translate")
    def test_translation_creation(self, mock_translate):
        mock_translate.return_value.text = "Translated question"
        faq = FAQ.objects.create(question="Test?", answer="Answer")
        self.assertEqual(faq.question_hi, "Translated question")
