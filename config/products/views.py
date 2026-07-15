from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from rest_framework.authentication import TokenAuthentication
from core.authentication import CsrfExemptSessionAuthentication
from core.permissions import IsStaffOrAdmin
# Create your views here.


class ProductListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsStaffOrAdmin()]
        return []

    def get_authenticators(self):
        return [TokenAuthentication(), CsrfExemptSessionAuthentication()]

    def get(self, request):
        status_filter = request.query_params.get('status', 'all')
        products = Product.objects.all()

        if status_filter == 'activated':
            products = products.filter(status='active')
        elif status_filter == 'expired':
            products = products.filter(status='inactive')
        # 'all' or anything else -> no filtering, return everything

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ProductDetailView(APIView):
    
    def get_permissions(self):
        if self.request.method  in ['PUT' , 'DELETE']:
            return [IsStaffOrAdmin()]
        return []
    
    
    def get_authenticators(self):
        return [TokenAuthentication() , CsrfExemptSessionAuthentication()]

    
    
    def get(self , request , pk):
        product = get_object_or_404(Product , pk=pk)
        serializer = ProductSerializer(product)
        return  Response(serializer.data)
    
    def put(self , request , pk):
        product = get_object_or_404(Product , pk=pk)
        serializer = ProductSerializer(product , data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self , request , pk):
        product = get_object_or_404(Product , pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    












# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
    
    
    

