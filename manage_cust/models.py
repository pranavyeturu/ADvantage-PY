from django.db import models
from django.utils import timezone
from user_auth.models import AdRequest



class Customer(models.Model):
    name   = models.CharField(max_length=120, blank=True)
    phone  = models.CharField(max_length=30, blank=True)
    email  = models.EmailField(unique=True)

    def __str__(self):
        return self.email

class CustomerUpload(models.Model):
    """
    Stores the original file; individual rows are turned into Customer
    objects immediately after save (see the post_save signal below).
    """
    file        = models.FileField(upload_to="uploads/customers/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} ({self.uploaded_at:%Y-%m-%d %H:%M})"

class SentEmail(models.Model):
    ad_request    = models.ForeignKey(AdRequest, on_delete=models.CASCADE)
    customer      = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    user          = models.ForeignKey("user_auth.CustomUser", on_delete=models.SET_NULL, null=True, blank=True)  # ✅ NEW
    email_address = models.EmailField()
    success       = models.BooleanField()
    error_message = models.TextField(blank=True)
    sent_at       = models.DateTimeField(default=timezone.now)

    def __str__(self):
        status = "✔" if self.success else "✘"
        return f"{status} {self.email_address} @ {self.sent_at:%Y-%m-%d %H:%M}"
