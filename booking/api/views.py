from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework import viewsets,status
from .serializers import UserBookingSerializer,AdminBookingSerializer
from booking.models import Booking
from rooms.models import Room
from .permissions import IsOwner
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from .pagination import BookingPagination





class BookingViewset(viewsets.ModelViewSet):

    queryset = Booking.objects.all()
    pagination_class = BookingPagination
    

    def get_serializer_class(self):
        
        if self.request.user.is_staff:
            return AdminBookingSerializer
        

        return UserBookingSerializer





    def get_permissions(self):
        
        if self.action in ['list','create','retrieve','cancel']:

            if self.action == 'cancel':
                return [IsOwner() | IsAdminUser()]

            return [IsAuthenticated()]
        
        elif self.action in ['update','partial_update','destroy']:
            
            return [IsAdminUser()]
        
        return [IsAdminUser()]
    



    
    def update_room_availability(self,room):

        active_bookings = room.bookings.filter(status__in=['pending','confirmed']).count()

        if room.room_type == 'single':
            
            capacity = 1
        
        elif room.room_type == 'double':

            capacity = 2
        
        else:
            capacity = 1
        
        if active_bookings >= capacity:
            room.status = 'occupied'
        
        else :
            room.status = 'available'

        room.save()



    
    

    def get_queryset(self):
        
        user = self.request.user

        if user.is_staff:

            return Booking.objects.all()
        
        return Booking.objects.filter(user=user)
    



    


    def perform_create(self, serializer):

        room_id = self.request.data.get('room')
        user = self.request.user
         
        if room_id:
            try:
                room = Room.objects.get(id=room_id)

                if Booking.objects.filter(room=room).exists():
                    
                    raise ValidationError('Booking can be done once.')


                if not room.is_available():
                    raise ValidationError("This room is not available for booking.")
                
                serializer.save(user=user, room=room, status='pending')



                self.update_room_availability(room)
            
            except Room.DoesNotExist:
                
                raise ValidationError('Room not found.')
            



            
    

    def perform_update(self, serializer):

        booking = self.get_object()
        old_status = booking.status
        update_booking = serializer.save(user=booking.user)

        if update_booking.room:

            self.update_room_availability(update_booking.room)
        
    




    def destroy(self, request, *args, **kwargs):

        booking = self.get_object()

        if booking.status == 'confirmed':

            raise PermissionDenied('Confirmed booking cannot be deleted. ')
        
        room = booking.room
        response =  super().destroy(request, *args, **kwargs)

        if room:
            self.update_room_availability(room)
        
        return response
    

    
    @action(detail=True, methods=['post'], permission_classes = [IsOwner | IsAdminUser])
    def cancel(self, request, pk=None):

        booking = self.get_object()

        if booking.status == 'confirmed':

            return Response({'message':'confirmed booking cannot be cancelled.'},status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'cancelled'
        booking.save()
        
        if booking.room:
            self.update_room_availability(booking.room)
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    

    
    @action(detail=True, methods=['post'], permission_classes = [IsAdminUser])
    def confirm(self, request, pk=None):

        booking = self.get_object()

        if booking.status == 'cancelled' or booking.status =='confirmed':
            return Response({'message':' cancelled or confirmed booking cannot be confirmed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'confirmed'

        booking.save()

        room = booking.room

        if room:  
            room.status = 'occupied'
            room.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
        