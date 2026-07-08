from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import OfferSerializer
from .models import Offer
# Create your views here.


class OfferListCreateView(APIView):
    def get(self , request):
        offers = Offer.objects.all()
        serializer = OfferSerializer(offers , many= True)
        return Response(serializer.data)
    
    
    def post(self , request):
        serializer = OfferSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    
class OfferDetailView(APIView):
    def get(self , request , pk):
        offers = get_object_or_404(Offer ,pk=pk)
        serializer = OfferSerializer(offers)
        return Response(serializer.data)

    def put(self , request , pk):
        offers  = get_object_or_404(Offer , pk=pk)
        serializer = OfferSerializer(offers , data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self , request , pk):
        offers = get_object_or_404(Offer ,pk=pk)
        offers.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self , request , pk):
        offers  = get_object_or_404(Offer , pk=pk)
        serializer = OfferSerializer(offers , data = request.data , partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    