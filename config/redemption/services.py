from django.utils import timezone
from datetime import timedelta
from .models import RedemptionRecord, QRCode


MEMBERSHIP_LIMITS = {
    'silver': 1,
    'silver_plus': 2,
    'gold': 3,
    'platinum': 4,
}


def mock_wallet_check(customer, points_required):
    """
    Mock version of checking wallet balance.
    Real IMS API would be called here in the future.
    """
    return customer.wallet_points >= points_required


def mock_deduct_points(customer, points):
    """
    Mock version of deducting wallet points.
    """
    customer.wallet_points -= points
    customer.save()
    return customer.wallet_points


def generate_qr_for_redemption(redemption_record, expiry_minutes=60):
    """
    Creates a QRCode object linked to a redemption record.
    """
    qr = QRCode.objects.create(
        redemption_record=redemption_record,
        expires_at=timezone.now() + timedelta(minutes=expiry_minutes)
    )
    return qr


def mock_create_invoice(redemption_record):
    """
    Mock version of invoice generation.
    """
    invoice_number = f"INV-{redemption_record.id}-{int(timezone.now().timestamp())}"
    redemption_record.invoice_number = invoice_number
    redemption_record.save()
    return invoice_number


def validate_qr_code(code):
    """
    Returns (qr_object, error_message)
    error_message is None if valid.
    """
    try:
        qr = QRCode.objects.get(code=code)
    except QRCode.DoesNotExist:
        return None, "Invalid QR code"

    if qr.is_used:
        return None, "QR code already used"

    if qr.is_expire():
        return None, "QR code has expired"

    return qr, None


def check_offer_validity(offer , customer):
    """
    Checks the offer is active and within its date range.
    """
    today = timezone.now().date()

    if offer.status != 'active':
        return False, "Offer is not Active"

    if today < offer.start_date or today > offer.end_date:
        return False, "Offer is not in valid range"
    
    if offer.membership_eligibility:
        eligible_tiers = [tier.strip().lower()  for tier in offer.membership_eligibility.split(',')]
        if customer.membership_level.lower()  not in eligible_tiers:
            return False, f"This offer is only available for {offer.membership_eligibility} members"

    return True, None


def check_membership_redemption_limit(customer, offer):
    """
    Checks redemption count against BOTH:
    - the offer's own redemption_limit field
    - the membership tier's general limit
    Whichever is stricter (smaller) wins.
    """
    tier_limit = MEMBERSHIP_LIMITS.get(customer.membership_level, 1)
    effective_limit = min(tier_limit, offer.redemption_limit)

    redemption_count = RedemptionRecord.objects.filter(
        customer=customer,
        offer=offer,
        status__in=['completed', 'scanned', 'invoice_created']
    ).count()

    return redemption_count < effective_limit