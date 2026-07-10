from rest_framework import serializers
from .models import Customer



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        extra_kwargs = {'password' :{'write_only' : True}}
        
        
        
class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name' , 'email' ,'phone' ,'password' ,'membership_level']
        extra_kwargs = {'password': {'write_only':True}}
        
    
    def create(self , validated_data):
        password = validated_data.pop("password")
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()
        return customer
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)