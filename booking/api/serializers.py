from rest_framework import serializers
from booking.models import Booking
##from rooms.models import Room
from datetime import date


class UserBookingSerializer(serializers.ModelSerializer):

    class Meta:

        model = Booking
        fields = ['duration','start_date','amount','room']
        read_only_fields = ['id','user','status','end_date','created_at']
    
    def validate_start_date(self,value):

        if value < date.today():
            raise serializers.ValidationError('Start date cannot be in past.')
        
        return value
    

    def validate_amount(self,value):
        

        if value <= 0:
            raise serializers.ValidationError('Amount Should be greater than 0.')
        
        
        return value
    
    def validate_duration(self,value):

        valid_duration = [choice[0] for choice in Booking.DURATION_CHOICES]

        if value not in valid_duration:
            raise serializers.ValidationError('Invalid Duration.')
        
        return value

class AdminBookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields =  ['duration','start_date','amount','room','status']
        read_only_fields = ['id','user','end_date','created_at','updated_at']
    
    def validate_status(self, value):

        allowed_status = [choice[0] for choice in Booking.STATUS_CHOICES]

        if value not in allowed_status:
            raise serializers.ValidationError('Invalid Status.')
        
        return value

          