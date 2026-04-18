from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.home, name='products'),
    path('almirah/', views.almirah, name='almirah'),
    path('cooler/', views.cooler, name='coller'),
    path('trunk/', views.trunk, name='trunk'),
    path('stand/', views.stand, name='stand'),
    path('authenticity/', views.authenticity, name='authenticity'),
    path('authenticity/verify/', views.verify_serial, name='verify_serial'),
    path('about/', views.about, name='about'),
    path('complain/', views.complain, name='complain'),
    path('contact/', views.contact, name='contact'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/toggle/', views.toggle_cart_item, name='toggle_cart_item'),
    path('buy-now/<int:product_id>/', views.buy_now_checkout, name='buy_now_checkout'),
    path('payments/razorpay-callback/', views.razorpay_payment_callback, name='razorpay_payment_callback'),
    path('payment-success/<int:order_id>/', views.order_success, name='order_success'),
    path('track_order/', views.track_order, name='track_order'),
    path('track_complain/', views.track_complain, name='track_complain'),
]
