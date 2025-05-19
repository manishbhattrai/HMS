from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room
from datetime import timedelta
from django.core.validators import MinValueValidator
# Create your models here.


class Booking(models.Model):

    DURATION_CHOICES = [
        ('one','1 Month'),
        ('three', '3 Month'),
        ('six', '6 Month'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    duration = models.CharField(max_length=15, choices=DURATION_CHOICES, default='one')
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default= 0.00)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):

        if self.start_date and not self.end_date:
            time_duration = {'one':1, 'three':3, 'six':6}.get(self.duration, 1)
            self.end_date = self.start_date + timedelta(days=30 * time_duration)

        super().save(*args, **kwargs)
    

    def __str__(self):
        return f" booking by {self.user.username} for room {self.room.room_number}"
    

        


