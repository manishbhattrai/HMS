from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rooms.models import Room
from .serializers import RoomSerializer
from rest_framework import viewsets



class RoomViewsets(viewsets.ModelViewSet):

    queryset = Room.objects.all()
    serializer_class = RoomSerializer


    def get_permissions(self):
        
        if self.action in ['list','retrieve']:

            return [IsAuthenticated()]
        
        elif self.action in ['create','update','partial_update','destroy']:
            
            return [IsAdminUser()]
        
        return [IsAdminUser()]
    

    

        
    
            
