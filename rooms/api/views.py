from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,filters
from rooms.models import Room
from .serializers import RoomSerializer
from rest_framework import viewsets
from .pagination import RoomPagination
from django_filters.rest_framework import DjangoFilterBackend



class RoomViewsets(viewsets.ModelViewSet):

    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    pagination_class = RoomPagination


    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_type','floor_number','status','has_ac','has_attached_bathroom']
    search_fields = ['room_number']
    ordering_fields = ['floor_number','monthly_rent']
    


    def get_permissions(self):
        
        if self.action in ['list','retrieve']:

            return [IsAuthenticated() ]
        
        elif self.action in ['create','update','partial_update','destroy']:
            
            return [IsAdminUser()]
        
        return [IsAdminUser()]
    
    def get_queryset(self):

        queryset = Room.objects.all()

        min_rent = self.request.query_params.get('min_rent')
        max_rent = self.request.query_params.get('max_rent')

        if min_rent:
            queryset = queryset.filter(monthly_rent__gte = min_rent)
        
        if max_rent:
            queryset = queryset.filter(monthly_rent__lte = max_rent)

        available_only = self.request.query_params.get('available_only')
        if available_only and available_only.lower() == 'true':
            queryset = queryset.filter(status='available')
        
        return queryset