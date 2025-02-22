# Generated by Django 5.1.5 on 2025-01-31 17:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("faqs", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="faq",
            name="question_bn",
        ),
        migrations.RemoveField(
            model_name="faq",
            name="question_hi",
        ),
        migrations.CreateModel(
            name="FAQTranslation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("language", models.CharField(max_length=10)),
                ("translated_text", models.TextField(blank=True)),
                (
                    "faq",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="faqs.faq",
                    ),
                ),
            ],
            options={
                "unique_together": {("faq", "language")},
            },
        ),
    ]
