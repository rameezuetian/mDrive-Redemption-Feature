from django.utils import timezone
from datetime import timedelta
from .models import RedemptionRecord ,QRCode

def mock_wallet_check(customer , points_required):
    """
    Mock version for IMS
    """
    return customer.wallet_points >= points_required


def  mock_deduct_points(customer , points):
    customer.wallet_points -= points
    customer.save()
    return customer.wallet_points


def generate_qr_for_redemption(redemption_record , expiry_minutes = 60):
    """
    Create  a QRcode object linked to a redemption record
    """
    qr = QRCode.objects.create(
        redemption_record=redemption_record,
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
    )
    

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
    Returns qr object and errors
    """
    try:
        qr = QRCode.objects.get(code = code)
    except QRCode.DoesNotExist:
        return None , "Invalid QR code"
    
    if qr.is_used():
        return None , "QR code already Used"
    
    if qr.is_expire():
        return None , "QR code Expired"
    
    return qr, None