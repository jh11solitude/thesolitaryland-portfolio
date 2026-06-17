from django.db import models

# ContactMessage Model
class ContactMessage(models.Model):
    """
    Stores every contact form submission.
    Persisted to DB first, then optionally emailed.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()

    # Admin workflow fields
    is_read = models.BooleanField(
        default=False,
        help_text="Mark as read once you've responded"
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']   # Newest messages first
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"From {self.name} <{self.email}> — {self.sent_at.strftime('%Y-%m-%d')}"