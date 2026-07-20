from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from rest_framework.response  import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import Partner
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.authentication import TokenAuthentication
from core.permissions import IsPartnerUser , IsSuperAdminUser , IsStaffOrAdmin
from core.authentication import CsrfExemptSessionAuthentication
from offers.models import Offer
from redemption.models import RedemptionRecord
from .permissions import IsAuthenticatedPartner
from .serializers import PartnerOfferSerializer

# Create your views here.

class PartnerLoginView(APIView):
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

        try:
            partner = user.partner_profile
        except Partner.DoesNotExist:
            return Response(
                {"error": "This account is not registered as a partner"},
                status=status.HTTP_403_FORBIDDEN
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "message": "Partner login successful",
                "token": token.key,
                "partner_id": partner.id,
                "company_name": partner.company_name,
                "redirect":"/partner-dashboard"
            },
            status=status.HTTP_200_OK
        )
        
        

class CreatePartnerView(APIView):
    """
    POST /api/partners/create/
    Super Admin only.
    Body: { "username": "...", "password": "...", "company_name": "...",
            "contact_email": "...", "contact_phone": "..." }
    """
    authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsSuperAdminUser]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        company_name = request.data.get('company_name')
        contact_email = request.data.get('contact_email')
        contact_phone = request.data.get('contact_phone', '')

        if not all([username, password, company_name, contact_email]):
            return Response(
                {"error": "username, password, company_name, and contact_email are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "This username is already taken"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create(
            username=username,
            password=make_password(password),
            is_staff=False,
            is_superuser=False
        )

        partner = Partner.objects.create(
            user=user,
            company_name=company_name,
            contact_email=contact_email,
            contact_phone=contact_phone
        )

        return Response(
            {
                "message": "Partner account created successfully",
                "partner_id": partner.id,
                "username": user.username,
                "company_name": partner.company_name
            },
            status=status.HTTP_201_CREATED
        )


class PartnerListView(APIView):
    """
    GET /api/partners/
    Super Admin only — lists all partners.
    """
    authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
    permission_classes = [IsStaffOrAdmin]

    def get(self, request):
        partners = Partner.objects.all()
        data = [
            {
                "id": p.id,
                "username": p.user.username,
                "company_name": p.company_name,
                "contact_email": p.contact_email,
                "contact_phone": p.contact_phone,
                "created_at": p.created_at
            }
            for p in partners
        ]
        return Response(data)
        
        
class MyOffersView(APIView):
    """
    GET /api/partners/my-offers/
    Partner only — returns only offers belonging to this partner,
    each with a redemption count.
    """
    authentication_classes = [TokenAuthentication , CsrfExemptSessionAuthentication]
    permission_classes = [IsPartnerUser]
    
    def get(self , request):
        partner = request.user.partner_profile
        offers = Offer.objects.filter(partner = partner)
        
        data = []
        
        for offer in offers:
            redemption_count = RedemptionRecord.objects.filter(
                offer=offer,
                status__in = ['completed' ,'scanned' ,'invoice_created']
            ).count()
            
            data.append({
                "id": offer.id,
                "title": offer.title,
                "category": offer.category,
                "description": offer.description,
                "status": offer.status,
                "start_date": offer.start_date,
                "end_date": offer.end_date,
                "redemption_limit": offer.redemption_limit,
                "membership_eligibility": offer.membership_eligibility,
                "total_redemptions": redemption_count
            })
        return Response(data)
    
    
class MyOfferRedemptionView(APIView):
    """
    GET /api/partners/my-offers/<offer_id>/redemptions/
    Partner only — detailed list of who redeemed a specific offer
    (only if that offer belongs to this partner).
    """
    
    authentication_classes = [TokenAuthentication  , CsrfExemptSessionAuthentication]
    permission_classes = [IsPartnerUser]
    
    
    def get(self , request , offer_id):
        partner = request.user.partner_profile
        offer = get_object_or_404(Offer, pk = offer_id , partner = partner)
        
        records = RedemptionRecord.objects.filter(
            offer = offer ,
            status__in = ['completed', 'scanned' , 'invoice_created']
        ).order_by('-created_at')
        
        data = [
            {
                "transaction_id": r.id,
                "redeemed_at": r.updated_at,
                "customer_name":r.customer.name,
                "status":r.status,
            }
            for r in records
        ]
        
        return Response({
            "offer_title":offer.title,
            "total_redemptions":len(data),
            "redemptions":data
        })
        

            
def partner_login_page(request):
    return render(request, 'partners/partner_login.html')


def partner_dashboard_page(request):
    return render(request, 'partners/partner_dashboard.html')

def partner_scan_page(request):
    return render(request, 'partners/partner_scan.html')

# def partner_reports_page(request):
#     return render(request, 'partners/partner_reports.html')


# def partner_manage_offers_page(request):
#     return render(request, 'partners/partner_manage_offers.html')









# class PartnerOfferListCreateView(APIView):
#     authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
#     permission_classes = [IsAuthenticatedPartner]

#     def get_partner(self, request):
#         return request.user.partner_profile

#     def get(self, request):
#         partner = self.get_partner(request)
#         status_filter = request.query_params.get("status")
#         search_query = request.query_params.get("q")
#         offers = Offer.objects.filter(partner=partner).order_by("-updated_at", "-id")

#         if status_filter:
#             offers = offers.filter(status=status_filter)

#         if search_query:
#             offers = offers.filter(title__icontains=search_query)

#         serializer = PartnerOfferSerializer(offers, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = PartnerOfferSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(partner=self.get_partner(request))
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class PartnerOfferDetailView(APIView):
#     authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
#     permission_classes = [IsAuthenticatedPartner]

#     def get_object(self, request, pk):
#         return get_object_or_404(
#             Offer.objects.filter(partner=request.user.partner_profile),
#             pk=pk,
#         )

#     def get(self, request, pk):
#         offer = self.get_object(request, pk)
#         serializer = PartnerOfferSerializer(offer)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         offer = self.get_object(request, pk)
#         serializer = PartnerOfferSerializer(offer, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save(partner=request.user.partner_profile)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         offer = self.get_object(request, pk)
#         offer.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class PartnerReportSummaryView(APIView):
#     authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
#     permission_classes = [IsAuthenticatedPartner]

#     def get(self, request):
#         partner = request.user.partner_profile
#         partner_offers = Offer.objects.filter(partner=partner)
#         completed_redemptions = RedemptionRecord.objects.filter(
#             offer__partner=partner,
#             status="completed",
#         )
#         today = timezone.now().date()

#         data = {
#             "total_offers": partner_offers.count(),
#             "active_offers": partner_offers.filter(
#                 status="active",
#                 start_date__lte=today,
#                 end_date__gte=today,
#             ).count(),
#             "inactive_offers": partner_offers.filter(status="inactive").count(),
#             "expired_offers": partner_offers.filter(end_date__lt=today).count(),
#             "completed_redemptions": completed_redemptions.count(),
#         }
#         return Response(data)


# class PartnerOfferStatusBreakdownView(APIView):
#     authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
#     permission_classes = [IsAuthenticatedPartner]

#     def get(self, request):
#         partner = request.user.partner_profile
#         rows = (
#             Offer.objects.filter(partner=partner)
#             .values("status")
#             .annotate(total=Count("id"))
#             .order_by("status")
#         )
#         return Response(list(rows))


# class PartnerOfferRedemptionBreakdownView(APIView):
#     authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
#     permission_classes = [IsAuthenticatedPartner]

#     def get(self, request):
#         partner = request.user.partner_profile
#         rows = (
#             RedemptionRecord.objects.filter(
#                 offer__partner=partner,
#                 status="completed",
#             )
#             .values("offer__id", "offer__title")
#             .annotate(total=Count("id"))
#             .order_by("-total", "offer__title")
#         )
#         return Response(list(rows))
