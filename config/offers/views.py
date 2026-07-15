from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone
from core.authentication import CsrfExemptSessionAuthentication
from core.permissions import IsStaffOrAdmin
from .serializers import OfferSerializer
from .models import Offer


class OfferListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsStaffOrAdmin()]
        return []

    def get_authenticators(self):
        return [TokenAuthentication(), CsrfExemptSessionAuthentication()]

    def get(self, request):
        status_filter = request.query_params.get('status', 'all')
        offers = Offer.objects.all()
        today = timezone.now().date()

        if status_filter == 'activated':
            offers = offers.filter(status='active', start_date__lte=today, end_date__gte=today)
        elif status_filter == 'expired':
            offers = offers.filter(end_date__lt=today)

        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsStaffOrAdmin()]
        return []

    def get_authenticators(self):
        return [TokenAuthentication(), CsrfExemptSessionAuthentication()]

    def get(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)
        serializer = OfferSerializer(offer)
        return Response(serializer.data)

    def put(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)
        serializer = OfferSerializer(offer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk)
        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)