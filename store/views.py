import json
import re
import uuid
from decimal import Decimal

import razorpay
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import ContactSubmission, Product, Complaint, Order, SliderImage, Review, SerialNumberRecord
from django.contrib import messages
from django.http import JsonResponse



def home(request):
    search_query = request.GET.get('search', '').strip()
    search_results = None
    related_products = None

    if search_query:
        search_results = Product.objects.filter(
            Q(name__icontains=search_query) |
            Q(tagline__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        ).distinct()

        if not search_results.exists():
            terms = re.findall(r"[\w\u0080-\uFFFF]+", search_query)
            for term in terms:
                related_products = Product.objects.filter(
                    Q(name__icontains=term) |
                    Q(tagline__icontains=term) |
                    Q(description__icontains=term)
                ).distinct()
                if related_products.exists():
                    break

            if not related_products or not related_products.exists():
                related_products = Product.objects.filter(
                    Q(name__icontains=search_query[:4]) |
                    Q(description__icontains=search_query[:4])
                ).distinct()[:12]

    slider_images = SliderImage.objects.filter(active=True).order_by('sort_order')
    special_offers = Product.objects.filter(featured_offer=True, image__isnull=False)
    popular_products = Product.objects.filter(featured_popular=True, image__isnull=False)
    almirah_products = Product.objects.filter(category='ALMIRAH', image__isnull=False).filter(
        Q(featured_homepage_almirah=True) | Q(featured_homepage=True)
    )
    cooler_products = Product.objects.filter(category='COOLER', image__isnull=False).filter(
        Q(featured_homepage_cooler=True) | Q(featured_homepage=True)
    )
    trunk_products = Product.objects.filter(category='TRUNK', image__isnull=False).filter(
        Q(featured_homepage_trunk=True) | Q(featured_homepage=True)
    )
    stand_products = Product.objects.filter(category='STAND', image__isnull=False).filter(
        Q(featured_homepage_stand=True) | Q(featured_homepage=True)
    )
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')[:12]
    return render(request, 'index.html', {
        'slider_images': slider_images,
        'special_offers': special_offers,
        'popular_products': popular_products,
        'almirah_products': almirah_products,
        'cooler_products': cooler_products,
        'trunk_products': trunk_products,
        'stand_products': stand_products,
        'reviews': reviews,
        'search_query': search_query,
        'search_results': search_results,
        'related_products': related_products,
    })


def cooler(request):
    items = Product.objects.filter(category='COOLER')
    return render(request, 'coller.html', {
        'items': items,
    })

def trunk(request):
    items = Product.objects.filter(category='TRUNK')
    return render(request, 'trunk.html', {
        'items': items,
    })

# --- Naye bache huye pages ke liye functions ---

def authenticity(request):
    return render(request, 'Authenticity.html')


def verify_serial(request):
    serial = request.GET.get('serial', '').strip()
    if not serial:
        return JsonResponse({
            'status': 'fail',
            'title': 'Verification Failed',
            'text': 'Please enter a valid serial number.',
        })

    record = SerialNumberRecord.objects.filter(serial_number__iexact=serial).first()
    if record:
        product_name = record.product.name if record.product else None
        product_type = record.product.category if record.product else None
        purchase_date = record.purchase_date.strftime('%Y-%m-%d') if record.purchase_date else None
        warranty_expiry = record.warranty_expiry.strftime('%Y-%m-%d') if record.warranty_expiry else None
        warranty_status = 'Unknown'
        if record.warranty_expiry:
            warranty_status = 'Active' if record.warranty_expiry >= timezone.localdate() else 'Expired'
        return JsonResponse({
            'status': 'success',
            'title': 'Authentic Product',
            'text': 'This serial number is registered to a genuine Sunil Trunk House product. Thank you for choosing quality!',
            'customer_name': record.customer_name,
            'product_type': product_type,
            'product_name': product_name,
            'purchase_date': purchase_date,
            'warranty_activate_date': purchase_date,
            'warranty_expiry_date': warranty_expiry,
            'warranty_status': warranty_status,
        })

    return JsonResponse({
        'status': 'fail',
        'title': 'Verification Failed',
        'text': 'This serial number is not found in our records. Please contact us at +91 6386569834 to report a fake product.',
    })


def about(request):
    return render(request, 'about_us.html')

def contact(request):
    if request.method == 'POST':
        ContactSubmission.objects.create(
            name=request.POST.get('name', '').strip(),
            email=request.POST.get('email', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            subject=request.POST.get('subject', '').strip(),
            message=request.POST.get('message', '').strip(),
        )
        messages.success(request, 'Your message has been received. We will contact you shortly.')
        return redirect('contact')
    return render(request, 'contact.html')

def track_order(request):
    query = request.GET.get('order_id')
    result = None
    if query:
        result = Order.objects.filter(order_number__iexact=query.strip()).first()
    return render(request, 'order_track.html', {'result': result, 'query': query})
def track_complain(request):
    query = request.GET.get('order_id')
    result = None

    if query:
        result = Complaint.objects.filter(serial_number=query).first()

    context = {
        'result': result,
        'query': query
    }
    return render(request, 'complain_tracker.html', context)


def get_cart_ids(request):
    cart = request.session.get('cart', [])
    return [int(item) for item in cart if str(item).isdigit()]


def cart(request):
    cart_ids = get_cart_ids(request)
    cart_items = Product.objects.filter(id__in=cart_ids)
    cart_total = sum(item.price for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            product_id = None

        if product_id and Product.objects.filter(id=product_id).exists():
            cart = request.session.get('cart', [])
            if product_id not in cart:
                cart.append(product_id)
                request.session['cart'] = cart

    return redirect(request.POST.get('next', request.META.get('HTTP_REFERER', '/')))


def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            product_id = None

        if product_id:
            cart = request.session.get('cart', [])
            cart = [item for item in cart if item != product_id]
            request.session['cart'] = cart

    return redirect('cart')


def toggle_cart_item(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except ValueError:
        payload = request.POST

    product_id = payload.get('product_id')
    try:
        product_id = int(product_id)
    except (TypeError, ValueError):
        product_id = None

    if not product_id or not Product.objects.filter(id=product_id).exists():
        return JsonResponse({'success': False, 'message': 'Invalid product ID.'}, status=400)

    cart = request.session.get('cart', [])
    if product_id in cart:
        cart = [item for item in cart if item != product_id]
        action = 'removed'
    else:
        cart.append(product_id)
        action = 'added'

    request.session['cart'] = cart
    return JsonResponse({'success': True, 'action': action, 'cart_count': len(cart)})


def get_razorpay_client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


def buy_now_checkout(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    product = get_object_or_404(Product, pk=product_id)
    if not product.is_in_stock:
        return JsonResponse({'success': False, 'message': 'Product is out of stock.'}, status=400)

    amount_in_paise = int(Decimal(str(product.price)) * 100)
    order_number = f"SH{uuid.uuid4().hex[:10].upper()}"

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except ValueError:
        payload = {}

    customer_name = payload.get('customer_name', '').strip()
    customer_phone = payload.get('customer_phone', '').strip()
    customer_address = payload.get('customer_address', '').strip()
    customer_email = payload.get('customer_email', '').strip()

    if not customer_name or not customer_phone or not customer_address:
        return JsonResponse({'success': False, 'message': 'Customer details are required.'}, status=400)

    client = get_razorpay_client()
    try:
        razorpay_order = client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': order_number,
            'payment_capture': 1,
            'notes': {
                'product_id': str(product.id),
                'product_name': product.name,
                'customer_name': customer_name,
                'customer_phone': customer_phone,
            },
        })
    except Exception as exc:
        # Catching all errors (Authentication, Network, etc.) to prevent server crash
        print('Razorpay order creation failed:', str(exc))
        error_msg = str(exc)
        if "Authentication failed" in error_msg:
            error_msg = "Razorpay authentication failed. Please check your API keys in settings.py."
        return JsonResponse({'success': False, 'message': error_msg}, status=400)

    order = Order.objects.create(
        order_number=order_number,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        customer_address=customer_address,
        product=product,
        quantity=1,
        product_details=f'{product.name} x 1',
        total_amount=product.price,
        razorpay_order_id=razorpay_order['id'],
    )

    return JsonResponse({
        'success': True,
        'razorpay_order_id': razorpay_order['id'],
        'amount': amount_in_paise,
        'currency': 'INR',
        'order_number': order.order_number,
        'product_name': product.name,
        'order_id': order.id,
    })


@csrf_exempt
def razorpay_payment_callback(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON payload.'}, status=400)

    razorpay_order_id = payload.get('razorpay_order_id')
    razorpay_payment_id = payload.get('razorpay_payment_id')
    razorpay_signature = payload.get('razorpay_signature')
    customer_name = payload.get('customer_name', '').strip()
    customer_phone = payload.get('customer_phone', '').strip()
    customer_address = payload.get('customer_address', '').strip()
    customer_email = payload.get('customer_email', '').strip()

    if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
        return JsonResponse({'success': False, 'message': 'Missing Razorpay payment fields.'}, status=400)

    order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
    if not order:
        return JsonResponse({'success': False, 'message': 'Order not found.'}, status=404)

    client = get_razorpay_client()
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        order.payment_status = 'Failed'
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.save(update_fields=['payment_status', 'razorpay_payment_id', 'razorpay_signature', 'updated_at'])
        return JsonResponse({'success': False, 'message': 'Payment signature verification failed.'}, status=400)

    try:
        with transaction.atomic():
            order.payment_status = 'Success'
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.transaction_date = timezone.now()
            order.customer_name = customer_name or order.customer_name
            order.customer_phone = customer_phone or order.customer_phone
            order.customer_address = customer_address or order.customer_address
            order.customer_email = customer_email or order.customer_email
            order.save(update_fields=[
                'payment_status',
                'razorpay_payment_id',
                'razorpay_signature',
                'transaction_date',
                'customer_name',
                'customer_phone',
                'customer_address',
                'customer_email',
                'updated_at',
            ])
            order.reduce_stock()
    except Exception as exc:
        order.payment_status = 'Failed'
        order.save(update_fields=['payment_status', 'updated_at'])
        return JsonResponse({'success': False, 'message': str(exc)}, status=400)

    return JsonResponse({
        'success': True,
        'redirect_url': reverse('order_success', args=[order.id]),
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, payment_status='Success')
    return render(request, 'order_success.html', {'order': order})


# Purane functions wese hi rahenge...

def almirah(request):
    # Saare products le kar aao jo ALMIRAH category mein hain
    items = Product.objects.filter(category='ALMIRAH')

    # Filter Logic: Agar user ne URL mein price ya search bheja hai
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('search')

    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)
    if search_query:
        items = items.filter(name__icontains=search_query)

    return render(request, 'almirah.html', {
        'items': items,
    })


def stand(request):
    # 1. Database se sirf wahi products nikalo jinki category 'STAND' hai
    items = Product.objects.filter(category='STAND')

    # 2. Search Logic (Naam se dhundhne ke liye)
    search_query = request.GET.get('search')
    if search_query:
        items = items.filter(name__icontains=search_query)

    # 3. Price Filter Logic
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)

    # 4. Sorting Logic (Low to High / High to Low)
    sort = request.GET.get('sort')
    if sort == 'p_low':
        items = items.order_by('price')
    elif sort == 'p_high':
        items = items.order_by('-price')
    elif sort == 'newest':
        items = items.order_by('-id')

    # 5. Data ko HTML (stand.html) par bhej do
    return render(request, 'stand.html', {
        'items': items,
    })

def complain(request):
    if request.method == "POST":
        Complaint.objects.create(
            customer_name=request.POST.get('name'),
            product_type=request.POST.get('product_type'),
            serial_number=request.POST.get('serial_number'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            purchase_date=request.POST.get('purchase_date'),
            bill_copy=request.FILES.get('bill_copy'),
            message=request.POST.get('message')
        )
        messages.success(request, "Your complaint was submitted successfully.")
        return redirect('complain')
    return render(request, 'complain.html')

