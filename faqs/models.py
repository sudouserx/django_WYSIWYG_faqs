import logging

from ckeditor.fields import RichTextField
from django.db import models
from googletrans import Translator

logger = logging.getLogger(__name__)


class FAQ(models.Model):
    question = models.TextField()  # English (default)
    answer = RichTextField()

    def get_translated_question(self, lang="en"):
        try:
            # Safely get or create translation
            translation, created = self.translations.get_or_create(language=lang)
        except Exception as e:
            logger.error(f"Database error for {lang}: {str(e)}")
            return self.question  # Fallback to English

        if created or not translation.translated_text:
            try:
                # Attempt translation
                translator = Translator()
                translated = translator.translate(self.question, dest=lang)
                translation.translated_text = translated.text
                translation.save()
            except Exception as e:
                logger.error(f"Translation failed for {lang}: {str(e)}")
                if created:  # Clean up empty translation if newly created
                    translation.delete()
                return self.question

        return translation.translated_text or self.question  # Final fallback


class FAQTranslation(models.Model):
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=10)  # e.g., 'hi', 'bn', 'fr'
    translated_text = models.TextField(blank=True)

    class Meta:
        unique_together = ("faq", "language")  # Prevent duplicate translations
