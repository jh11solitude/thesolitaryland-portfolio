from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    A ModelForm tied to ContactMessage.
    Django auto-generates validation from the model field types:
    - email must be a valid email address
    - name and message are required (not blank)
    - subject is optional (blank=True on the model)
    """

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            # Override default widgets with our cinematic CSS classes
            'name': forms.TextInput(attrs={
                'class': 'jk-form__input',
                'placeholder': 'Your name',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'jk-form__input',
                'placeholder': 'your@email.com',
                'autocomplete': 'email',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'jk-form__input',
                'placeholder': 'What is this about? (optional)',
            }),
            'message': forms.Textarea(attrs={
                'class': 'jk-form__textarea',
                'placeholder': 'Your message…',
                'rows': 6,
            }),
        }
        labels = {
            'name': 'Name',
            'email': 'Email',
            'subject': 'Subject',
            'message': 'Message',
        }
        error_messages = {
            'email': {
                'invalid': 'Please enter a valid email address.',
            },
        }