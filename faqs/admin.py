from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin

from .models import FAQ, FAQTranslation


class FAQTranslationInline(admin.TabularInline):
    model = FAQTranslation
    extra = 1  # Number of empty translation slots


class FAQAdminForm(forms.ModelForm):
    answer = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = FAQ
        fields = "__all__"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    form = FAQAdminForm
    inlines = [FAQTranslationInline]
    list_display = ("question", "answer")
