from rest_framework import serializers
from rooms.models import Room



class RoomSerializer(serializers.ModelSerializer):


    class Meta:
        model = Room
        fields = [

            'room_number','image','room_type','floor_number','total_bed',
            'monthly_rent','status','has_attached_bathroom','has_balcony','has_ac'
            
            ]
     
    def validate_room_number(self,value):

        instance = self.instance

        if Room.objects.filter(room_number=value).exists():
            if instance is None and instance.room_number != value:
                raise serializers.ValidationError('Room number must be unique.')
        
        return value
    
    def validate_monthly_rent(self, value):

        if value <= 0:
            raise serializers.ValidationError('Rent cannot be less than or equal to 0.')
        
        return value
    