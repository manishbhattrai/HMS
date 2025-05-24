from rest_framework import serializers
from users.models import Profile
from django.contrib.auth.models import User


##from django.contrib.auth import authenticate



class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only = True)
    password1 = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ['username','password','password1']

    
    def validate(self, data):

        password = data.get('password')
        password1 = data.get('password1')

        if len(password) < 8:
            raise serializers.ValidationError('Password must be more than 8 characters.')
        
        if password != password1:
            raise serializers.ValidationError('Password must match.')
        

        return data
    
    def create(self, validated_data):
        
        username = validated_data['username']
        password = validated_data.pop('password')
        validated_data.pop('password1')


        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()

        return user
    

class UserLoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(write_only = True)


    def validate(self, data):
        
        username = data.get('username')
        password = data.get('password')

        if username and password:
            
            if not User.objects.filter(username=username).exists():
                raise serializers.ValidationError('user with this username doesnot exists.')
        
        return data



class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['image','first_name','middle_name','last_name','email','date_of_birth','gender','address','phone_number']

    
    def validate_email(self, value):
        
        instance = self.instance

        if instance:
             
             if Profile.objects.filter(email=value).exclude(pk=instance.pk).exists():
                 raise serializers.ValidationError('Email already exists.')
        
        else:

            if Profile.objects.filter(email=value).exists():
                raise serializers.ValidationError('Email already exists.')
        
        return value


class ChangePasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(required = True)
    new_password = serializers.CharField(required = True)
    confirm_password = serializers.CharField(required = True)

    def validate(self, data):

        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("Password didn't match.")
        
        if len(new_password) < 8:
            raise serializers.ValidationError('Password should be more than 8 characters.')
        
        return data

class ForgotPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):
        


        try:
            profile = Profile.objects.get(email=value)
        
        except Profile.DoesNotExist:
            raise serializers.ValidationError('Email doesnot exists.')
        
        return value
    

class ResetPasswordSerializer(serializers.Serializer):

    new_password = serializers.CharField(write_only = True)


    def validate_new_password(self,value):

        if len(value) < 8:
            raise serializers.ValidationError('Password should be more than 8 characters.')
        
        return value
    
