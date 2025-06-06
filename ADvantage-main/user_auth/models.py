from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # Prevent login without a password

        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email, first_name, last_name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)  # Last name is required
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)  # Better for timestamps

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Returns the full name of the user."""
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        """Returns the first name of the user."""
        return self.first_name


class AdRequest(models.Model):
    user = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          on_delete=models.CASCADE,
                          related_name="ad_requests",
                          null=True,
                          blank=True,
                      )
    product = models.CharField(max_length=255)
    description = models.TextField()
    remarks = models.TextField(blank=True, null=True)
    tone = models.CharField(max_length=50)
    scope = models.CharField(max_length=50, blank=True,null=True,default="global")
    csv_file         = models.FileField(upload_to="uploads/csvs/", blank=True, null=True)
    include_hashtags = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    chosen_ad          = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.product