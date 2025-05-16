from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.



class Room(models.Model):

    ROOM_TYPE_CHOICES = [

        ('single','Single'),
        ('double','Double')
    ]

    STATUS_CHOICES = [

        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    ]

    room_number = models.CharField(max_length=100,unique=True)
    image = models.ImageField(upload_to='rooms/',null=True, blank=True)
    room_type = models.CharField(choices=ROOM_TYPE_CHOICES, default='single', null=False, blank=False, max_length=10)
    floor_number = models.PositiveIntegerField()
    total_bed = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    monthly_rent = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(choices=STATUS_CHOICES, default='available', max_length=15)
    has_attached_bathroom = models.BooleanField(default=False)
    has_balcony = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Room {self.room_number} - {self.get_room_type_display()}"
    
    def is_available(self):
        return self.status == 'available'

