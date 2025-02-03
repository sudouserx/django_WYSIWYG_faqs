import logging

from rest_framework import serializers

from .models import FAQ

logger = logging.getLogger(__name__)


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = self.context["request"].query_params.get("lang", "en")
        try:
            data["question"] = instance.get_translated_question(lang)
        except AttributeError:
            # Log warning and return default
            logger.warning(f"Missing translation for lang {lang} on FAQ {instance.id}")
            data["question"] = instance.question
        return data
