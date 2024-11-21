# models.py

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator

class UserVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6)
    verification_code_expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)



class GoogleUser(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    token_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    # Fields for the user profile
     # Regex validator for phone numbers
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
        message="Le numéro de téléphone doit être au format : '+999999999'. Jusqu'à 15 chiffres autorisés."
    )

    # Phone number field
    phone_number = models.CharField(max_length=17, validators=[phone_validator], blank=True, null=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, null=True,  blank=True)
    state = models.CharField(max_length=100, null=True,  blank=True)
    address = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True,  blank=True)



    # Timestamp for when the profile was created
    created_at = models.DateTimeField(default=timezone.now)

    def imageUrl(self):
        return f"http://localhost:8000/api/media/{self.profile_picture}"

    def __str__(self):
     
        return f"{self.firstname}"
      

class GoogleUserProfile(models.Model):
    
 # Regex validator for phone numbers
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
        message="Le numéro de téléphone doit être au format : '+999999999'. Jusqu'à 15 chiffres autorisés."
    )

    # Phone number field
    phone_number = models.CharField(max_length=17, validators=[phone_validator], blank=True, null=True)
    user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE, null=True,  blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, null=True,  blank=True)
    state = models.CharField(max_length=100, null=True,  blank=True)
    address = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_google_pictures/', blank=True, null=True)
  
    # Timestamp for when the profile was created
    created_at = models.DateTimeField(default=timezone.now)

   

    def imageUrl(self):
        return f"http://localhost:8000/api/media/{self.profile_picture}"


    def __str__(self):
     
        return f"Google User Profile {self.user.name}"
    
class Interest(models.Model):
    name = models.CharField(max_length=1000)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="interests")

    def __str__(self):
        return f"{self.name} {self.user.username}"


class InterestGoogle(models.Model):
    user = models.OneToOneField(GoogleUser, on_delete=models.CASCADE, null=True,  blank=True)
    name = models.CharField(max_length=1000)

    def __str__(self):
        return f"Google User {self.name}"

    




class UserProperty(models.Model):
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
        message="Le numéro de téléphone doit être au format : '+999999999'. Jusqu'à 15 chiffres autorisés."
    )

    # Phone number field
    property_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,  blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2,  null=True,  blank=True)
    type = models.CharField(max_length=1000)  # e.g., "Apartment", "House", "Office", etc.
    is_archived = models.BooleanField(default=False)
    status = models.CharField(max_length=10, default='open')
    country = models.CharField(max_length=100, default="country")
    state = models.CharField(max_length=255, null=True,  blank=True)
    city = models.CharField(max_length=255, null=True,  blank=True)
    address = models.CharField(max_length=255)
    category = models.CharField(max_length=1000, default="category")
    currency = models.CharField(max_length=25, null=True,  blank=True)
    decision = models.CharField(max_length=255, null=True,  blank=True)
    status = models.CharField(max_length=25, default="open")
    new_phone_number = models.CharField(max_length=17, validators=[phone_validator], blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    

# GoogleUser Property

class GoogleUserProperty(models.Model):
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',  # Example regex for international phone numbers
        message="Le numéro de téléphone doit être au format : '+999999999'. Jusqu'à 15 chiffres autorisés."
    )

    property_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE, null=True,  blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2,  null=True,  blank=True)
    type = models.CharField(max_length=1000)  # e.g., "Apartment", "House", "Office", etc.
    is_archived = models.BooleanField(default=False)
    status = models.CharField(max_length=10, default='open')
    country = models.CharField(max_length=100, default="country")
    state = models.CharField(max_length=255, null=True,  blank=True)
    city = models.CharField(max_length=255, null=True,  blank=True)
    address = models.CharField(max_length=255)
    category = models.CharField(max_length=1000, default="category")
    decision = models.CharField(max_length=255, null=True,  blank=True)
    currency = models.CharField(max_length=25, null=True,  blank=True)
    status = models.CharField(max_length=25, default="open")
    new_phone_number = models.CharField(max_length=17, validators=[phone_validator], blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    



# Google PROPERTY IMAGE


class GooglePropertyImage(models.Model):
    property = models.ForeignKey(GoogleUserProperty, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='google_property_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"


#  PROPERTY IMAGE

class PropertyImage(models.Model):
    property = models.ForeignKey(UserProperty, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"
    
    def imageUrl(self):
        return f"http://localhost:8000/api/media/{self.image}"

    





class Like(models.Model):
    USER_TYPE_CHOICES = [
        ('regular', 'Regular User'),
        ('google', 'Google User'),
    ]

    PROPERTY_TYPE_CHOICES = [
        ('regular', 'Regular Property'),
        ('google', 'Google Property'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    google_user = models.ForeignKey(GoogleUser, on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    property = models.ForeignKey(UserProperty, on_delete=models.CASCADE, null=True, blank=True)
    google_property = models.ForeignKey(GoogleUserProperty, on_delete=models.CASCADE, null=True, blank=True)
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPE_CHOICES)

    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'google_user', 'property', 'google_property')






class Subscription(models.Model):
    # Defining user type choices
    USER_TYPE_CHOICES = [
        ('regular', 'Regular User'),
        ('google', 'Google User'),
    ]

    # Foreign keys for regular users and Google users
    user = models.ForeignKey(User, related_name='subscriptions', on_delete=models.CASCADE, null=True, blank=True)
    google_user = models.ForeignKey(GoogleUser, related_name='google_subscriptions', on_delete=models.CASCADE, null=True, blank=True)

    # Subscriptions to another user (either regular or Google user)
    subscribed_to_user = models.ForeignKey(User, related_name='subscribers', on_delete=models.CASCADE, null=True, blank=True)
    subscribed_to_google_user = models.ForeignKey(GoogleUser, related_name='google_subscribers', on_delete=models.CASCADE, null=True, blank=True)

    
    # To distinguish between regular and Google user/property
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
   

    # Track when the subscription was made
    subscribed_at = models.DateTimeField(auto_now_add=True)

    # Ensure uniqueness between user subscriptions and properties
    class Meta:
        unique_together = (
            ('user','google_user',  'subscribed_to_user', 'subscribed_to_google_user'),
           
        )

