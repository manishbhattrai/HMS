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

        if Profile.objects.filter(email=value).exists():
            if instance is None or instance.email != value:
                raise serializers.ValidationError('Email already exists.')
        
        return value
