import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Customer
from .serializers import CustomerSerializer , SignUpSerializer ,LoginSerializer
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # skip CSRF check entirely


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
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []
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
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []
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
        
class AddWalletPointsView(APIView):
    """
    POST /api/customers/<id>/add-points/
    Mock endpoint simulating IMS crediting wallet points after a purchase.
    Body: { "points": 200 }
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []
    def post(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        points = request.data.get('points')

        if not points or not isinstance(points, (int, float)) or points <= 0:
            return Response(
                {"error": "A positive 'points' value is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        customer.wallet_points += int(points)
        customer.save()

        return Response(
            {
                "message": f"{points} points added successfully",
                "customer_id": customer.id,
                "new_balance": customer.wallet_points
            },
            status=status.HTTP_200_OK
        )
        
        


class AdminLoginView(APIView):
    """
    POST /api/auth/admin-login/
    Body: { "username": "admin", "password": "adminpass" }
    """
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_staff:
            return Response(
                {"error": "This account does not have admin access"},
                status=status.HTTP_403_FORBIDDEN
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "Admin login successful",
                "token": token.key,
                "username": user.username
            },
            status=status.HTTP_200_OK
        )   
        
        
def admin_login_page(request):
    return render(request, 'admin_login.html')

def admin_summary_page(request):
    return render(request, 'admin_summary.html')
        
        
def signup_page(request):
    return render(request , 'signup.html')

def login_page(request):
    return render(request , 'login.html')

def product_page(request):
    return render(request , 'products.html')

def qr_page(request):
    return render(request , 'qr.html')

def offers_pages(request):
    return render(request , 'offers.html')


def history_page(request):
    return render(request , 'history.html')

def outlet_scan_page(request):
    return render(request, 'outlet_scan.html')
