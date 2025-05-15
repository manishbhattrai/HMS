from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):

    GENDER_CHOICE = [
        
        ('m','Male'),
        ('f','Female')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile/')
    first_name = models.CharField(max_length=255, null=False, blank=False)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(choices=GENDER_CHOICE, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    phone_number = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):

        return f"{self.user.username}'s profile."








