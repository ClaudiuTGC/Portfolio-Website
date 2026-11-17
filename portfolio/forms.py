from django import forms
from django.core.exceptions import ValidationError


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"autocomplete": "name"}))
    email = forms.EmailField(
        max_length=254, widget=forms.EmailInput(attrs={"autocomplete": "email"})
    )
    message = forms.CharField(max_length=4000, widget=forms.Textarea(attrs={"rows": 5}))
    website = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"})
    )

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise ValidationError("Leave this field blank.", code="honeypot")
        return ""
