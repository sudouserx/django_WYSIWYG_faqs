import logging

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from googletrans import Translator

from .models import FAQ, FAQTranslation

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(Exception,), max_retries=3)
def translate_faq_language(faq_id, target_lang):
    try:
        faq = FAQ.objects.get(id=faq_id)
        translation, _ = FAQTranslation.objects.get_or_create(
            faq=faq, language=target_lang
        )
        if not translation.translated_text:
            translator = Translator()
            result = translator.translate(faq.question, dest=target_lang)
            translation.translated_text = result.text
            translation.save()
    except ObjectDoesNotExist:
        logger.error(f"FAQ {faq_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Translation task failed: {str(e)}")
        raise
