import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Customer
from .serializers import CustomerSerializer , SignUpSerializer ,LoginSerializer


class CustomerListCreateView(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailView(APIView):
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def put(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
class SignupView(APIView):
    """
    POST /api/auth/signup/
    """
    def post(self , request):
        serializer = SignUpSerializer(data= request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(
                {
                "message" : "Signup Successfully",
                "customer_id":customer.id,
                "name":customer.name,
                "email":customer.email,
            },
                status = status.HTTP_201_CREATED
                )
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    

class LoginView(APIView):
    """
    POST /api/auth/login
    """
    def  post(self , request):
        serializer = LoginSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors  , status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try :
            customer = Customer.objects.get(email= email)
        except Customer.DoesNotExist:
            return Response({"error":"Invalid email or password"},status=status.HTTP_400_BAD_REQUEST)
        if not customer.check_password(password):
            return Response({"error":"Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(
            {
                "message": "Login successful",
                "customer_id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "wallet_points": customer.wallet_points,
                "membership_level": customer.membership_level
            },
            status= status.HTTP_200_OK
        )