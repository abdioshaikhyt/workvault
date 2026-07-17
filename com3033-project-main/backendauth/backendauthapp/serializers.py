from rest_framework import serializers
from .models import Practice
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from django_altcha import AltchaField
from altcha import verify_solution                                    
from django.conf import settings                                           
import base64                                                             
import json                                                               
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    captcha = AltchaField()
    practice_name = serializers.CharField(write_only=True) 
    practice_display_name = serializers.SerializerMethodField()
    

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password", "is_active", "is_staff", "practice_name", "practice_display_name", "practice_superuser"]
        extra_kwargs = {
            "password": {"write_only": True},
            "is_active": {"default": True}
        }

    def get_practice_display_name(self, obj):
        return obj.practice_id.practice_name if obj.practice_id else ''

    def validate_practice_name(self, value):
        if not Practice.objects.filter(practice_name=value).exists():
            raise ValidationError("Practice with this name does not exist.")
        return value

    def validate(self, attrs):
      captcha_token = self.initial_data.get("captcha")                             
      if not captcha_token:                                                           
        raise ValidationError({"captcha": ["CAPTCHA token is required."]})            

      try:                                                                            
        decoded = json.loads(base64.b64decode(captcha_token).decode())               
      except Exception:                                                              
        raise ValidationError({"captcha": ["Invalid CAPTCHA token format."]})            

      ok, err = verify_solution(decoded, settings.ALTCHA_HMAC_KEY, check_expires=True)  
      if err:                                                                        
        print("Error:", err)                                                       
        raise ValidationError({"captcha": ["Invalid CAPTCHA token format."]})          
      elif ok:                                                                       
        print("Solution verified!")                                              
      else:                                                                         
        print("Invalid solution.")                                                     
        raise ValidationError({"captcha": ["Invalid CAPTCHA solution."]})              

      password = attrs.get("password")
      if password is not None:
        try:
          validate_password(password)
        except DjangoValidationError as e:
          raise ValidationError({"password": list(e.messages)})
      return attrs

    def create(self, validated_data):
        practice_name = validated_data.pop('practice_name', None)
        validated_data.pop('is_active', None)
        validated_data.pop("captcha", None) 
        
        user = User.objects.create_user(**validated_data, is_active = False)
        
        if practice_name:
            
            practice = Practice.objects.get(practice_name=practice_name)
            user.practice_id = practice
            user.save()
           
        return user

class UserUpdateSerializer(serializers.ModelSerializer):            
    practice_display_name = serializers.SerializerMethodField()       
    
    class Meta:                                           
        model = User                                        
        fields = ["id", "username", "first_name", "last_name", "email", "password", "is_active", "is_staff", "practice_display_name", "practice_superuser"]  
        extra_kwargs = {                               
            "password": {"write_only": True},                  
            "is_active": {"default": True}                 
        }                                                   

    def get_practice_display_name(self, obj):                           
        return obj.practice_id.practice_name if obj.practice_id else ''     

    def validate(self, attrs):                                 
      password = attrs.get("password")                         
      if password is not None:                                 
        try:                                                    
          validate_password(password)                             
        except DjangoValidationError as e:                    
          raise ValidationError({"password": list(e.messages)}) 
      return attrs                                          

    def update(self, instance, validated_data):                
        password = validated_data.pop("password", None)        
        for attr, value in validated_data.items():             
            setattr(instance, attr, value)                  
        if password:                                      
            try:                                         
                validate_password(password, user=instance)           
            except DjangoValidationError as e:                        
                raise ValidationError({"password": list(e.messages)})    
            instance.set_password(password)                            
        instance.save()                                                  
        return instance                                                  

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    captcha = AltchaField()                     
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username  
        token['is_staff'] = user.is_staff
        token['practice_id'] = user.practice_id.id if user.practice_id else None
        token['practice_superuser'] = user.practice_superuser
        return token
   
    def validate(self, attrs):
        captcha_token = self.initial_data.get("captcha")                             
        if not captcha_token:                                                           
            raise ValidationError({"captcha": ["CAPTCHA token is required."]})            

        try:                                                                         
            decoded = json.loads(base64.b64decode(captcha_token).decode())           
        except Exception:                                                            
            raise ValidationError({"captcha": ["Invalid CAPTCHA token format."]})      

        ok, err = verify_solution(decoded, settings.ALTCHA_HMAC_KEY, check_expires=True)  
        if err:                                                                     
            print("Error:", err)                                               
            raise ValidationError({"captcha": ["Invalid CAPTCHA token format."]})       
        elif ok:                                                                    
            print("Solution verified!")                                       
        else:                                                                     
            print("Invalid solution.")                                      
            raise ValidationError({"captcha": ["Invalid CAPTCHA solution."]})       
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            raise AuthenticationFailed("Incorrect username or password.")

        if not user.is_active:
            raise AuthenticationFailed("Awaiting verification.")

        return super().validate(attrs)
    
       
class PracticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practice
        fields = ['id', 'practice_name']