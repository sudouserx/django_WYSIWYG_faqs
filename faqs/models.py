from ckeditor.fields import RichTextField
from django.db import models
from googletrans import Translator


class FAQ(models.Model):
    question = models.TextField()  # English (default)
    answer = RichTextField()

    def get_translated_question(self, lang="en"):
        # Get or create translation for the requested language
        translation, created = self.translations.get_or_create(language=lang)
        if created or not translation.translated_text:
            # Auto-translate and save if missing
            try:
                translator = Translator()
                translated = translator.translate(self.question, dest=lang)
                translation.translated_text = translated.text
                translation.save()
            except Exception:
                return self.question  # Fallback to English
        return translation.translated_text


class FAQTranslation(models.Model):
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name="translations")
    language = models.CharField(max_length=10)  # e.g., 'hi', 'bn', 'fr'
    translated_text = models.TextField(blank=True)

    class Meta:
        unique_together = ("faq", "language")  # Prevent duplicate translations
