from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm


class ContactView(FormView):
    """
    Renders the contact form (GET) and processes submission (POST).

    On success:
      1. Save ContactMessage to database (never lose an enquiry)
      2. Send email notification to site owner
      3. Show Django flash message
      4. Redirect to same page (POST-Redirect-GET pattern)

    POST-Redirect-GET (PRG) pattern:
      After a successful POST, we redirect instead of rendering directly.
      This prevents the browser from resubmitting the form if the user
      refreshes the page — a classic UX problem.
    """
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:contact')

    def form_valid(self, form):
        """Called when form passes all validation."""

        # 1. Save to database FIRST — before email attempt
        contact_msg = form.save()

        # 2. Send email notification (may fail — that's okay, DB row is safe)
        try:
            send_mail(
                subject=f"New contact message from {contact_msg.name}: {contact_msg.subject or 'No subject'}",
                message=(
                    f"From: {contact_msg.name} <{contact_msg.email}>\n\n"
                    f"{contact_msg.message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=True,
                # fail_silently=True means email errors won't crash the view
                # The DB record ensures you never lose the message
            )
        except Exception:
            pass  # Email failure is non-fatal

        # 3. Flash success message
        messages.success(
            self.request,
            "Your message has been received. I'll be in touch soon."
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        """Called when form has validation errors."""
        messages.error(
            self.request,
            "Please check the form and try again."
        )
        return super().form_invalid(form)