from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import  APIView
from rest_framework.generics import CreateAPIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny,IsAuthenticated, IsAdminUser
from .serializers import (
                    UserRegistrationSerializer, UserLoginSerializer,
                    UserProfileSerializer, ChangePasswordSerializer,ForgotPasswordSerializer,
                    ResetPasswordSerializer
                    
                    )
from users.models import Profile,ResetPasswordToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsOwner
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError



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
    


class ForgotPasswordView(APIView):

    def post(self, request):

        data = request.data

        serializer = ForgotPasswordSerializer(data=data)

        if serializer.is_valid():

            email = serializer.validated_data['email']

            try:
                profile = Profile.objects.get(email=email)
                user = profile.user

            except Profile.DoesNotExist:
                return Response({"message": "If this email is registered, a reset link has been sent."}, status=status.HTTP_200_OK)
            

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))


            expire_at = timezone.now() + timedelta(hours=1)

            reset_token = ResetPasswordToken.objects.create(

                user = user,
                token = token,
                expire_at= expire_at
            )

            reset_link = f'http://localhost:8000/api/auth/reset-password/{uid}/{token}/'

            send_mail(
                'Password Reset Request',
                f'click the link to reset your password: {reset_link}',
                'hms@gmail.com',
                [email],
                fail_silently=False,
            )

            return Response({"message": "If this email is registered, a reset link has been sent."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

class ResetPasswordView(APIView):

    def post(self, request, uid, token):

        
        try:
            
            uid = urlsafe_base64_decode(uid).decode('utf-8')  
            user = User.objects.get(pk=uid)  
        except (ValueError, User.DoesNotExist):
            return Response({"message": "Invalid link or expired token."}, status=status.HTTP_400_BAD_REQUEST)


        try:
            reset_token = ResetPasswordToken.objects.get(user=user, token=token)

            if reset_token.is_expired():  
                raise ValidationError("Token has expired.")
            
        except ResetPasswordToken.DoesNotExist:

            return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        

        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            reset_token.delete()

            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)