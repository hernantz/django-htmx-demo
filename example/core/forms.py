from django import forms
from django.core.exceptions import ValidationError


class OddNumberForm(forms.Form):
    number = forms.IntegerField()


class SignupForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=100)
    email = forms.EmailField(label='Your email', max_length=100)
    repeat_email = forms.EmailField(label='Repeat your email', max_length=100)

    def clean_repeat_email(self):
        if self.cleaned_data.get('email') != self.cleaned_data.get('repeat_email'):
            raise ValidationError("Emails must match!")
        return self.cleaned_data['repeat_email']
