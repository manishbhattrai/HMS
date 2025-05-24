from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import  APIView
from rest_framework.generics import CreateAPIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, ChangePasswordSerializer
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsOwner
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError



class UserRegistrationView(CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserLoginView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):

        data = request.data

        serializer = UserLoginSerializer(data=data)
        
        if serializer.is_valid():

            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:

                refresh = RefreshToken.for_user(user)

                return Response(
                    {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)

                    }, status=status.HTTP_200_OK
                )
            return Response({"message":"Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):

        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"status": "success", "message": "User logged out successfully."}, status=status.HTTP_200_OK)
        
        except TokenError:
            return Response({"status": "error", "message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    
class UserProfileView(viewsets.ModelViewSet):

    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer
    

    def get_permissions(self):
        
        permissions = []

        if self.action == 'list':

            permissions = [IsAdminUser]
        
        elif self.action == 'create':

            permissions = [IsAuthenticated]
        
        elif self.action in ['update', 'partial_update']:

            permissions = [IsOwner | IsAdminUser]
        
        elif self.action == 'retrieve':
            
            permissions = [IsOwner | IsAdminUser]
        
        elif self.action == 'destroy':

            permissions = [ IsOwner | IsAdminUser]
        
        return  [permission() for permission in permissions]
    

    def perform_create(self, serializer):

        user = self.request.user
        
        serializer.save(user=user)

        
    
    def get_queryset(self):

        user = self.request.user
        
        if user.is_authenticated:

            if user.is_staff:  
                return Profile.objects.all()
        
            return Profile.objects.filter(user=user)
        else:
            return Profile.objects.none()
    

    
    def perform_update(self, serializer):
        
       user = self.request.user
       
       serializer.save(user=user)

    def perform_destroy(self, instance):
        
        user = self.request.user

        if instance.user != user:
            raise PermissionDenied('you can only delete your profile.')
        
        
        instance.delete()


class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        data = request.data
        serializer = ChangePasswordSerializer(data = data)


        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(current_password):
            return Response({'message':"Invalid Password."}, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(new_password)
        user.save()

        return Response({'message':'password changed successfully.'},status=status.HTTP_200_OK)
        
        
    



        

    
    