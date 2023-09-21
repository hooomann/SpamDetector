from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model extending AbstractUser
class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)  # Additional field to store user's phone number

# Model for a user's phonebook entries
class Phonebook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign key relationship with User model
    name = models.CharField(max_length=100, default="user_def")  # Name of the contact
    phone_number = models.CharField(max_length=15, default="123456789")  # Phone number of the contact

    def __str__(self):
        return f"Phonebook for {self.user.username}"

# Model to store contact information, whether registered or not
class ContactInformation(models.Model):
    name = models.CharField(max_length=100)  # Name of the contact
    phone_number = models.CharField(max_length=15)  # Phone number of the contact
    email = models.EmailField(null=True, blank=True)  # Email address of the contact (optional)
    spam_reports = models.PositiveIntegerField(default=0)  # Count of spam reports for the contact
    search_counts = models.PositiveIntegerField(default=0)  # Count of times contact has been searched
    is_registered = models.BooleanField(default=False)  # Indicates whether the contact is a registered user

    def __str__(self):
        return f"{self.name} ({self.phone_number})" 
