from django.conf import settings
from .models import Product


def cart_context(request):
    cart = request.session.get('cart', [])
    cart_ids = [int(item) for item in cart if str(item).isdigit()]
    return {
        'cart_count': len(cart_ids),
        'cart_ids': cart_ids,
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
        'razorpay_merchant_key': getattr(settings, 'RAZORPAY_KEY_ID', ''),
    }
