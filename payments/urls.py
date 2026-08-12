from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_page, name='payment_page'),
    path('pay/<str:reference>/', views.payment_gateway, name='payment_gateway'),
    path('binance/order/<str:reference>/', views.binance_create_order, name='binance_order'),
    path('verify/flutterwave/<str:reference>/', views.verify_flutterwave, name='verify_flutterwave'),
    path('verify/paystack/<str:reference>/', views.verify_paystack, name='verify_paystack'),
    path('webhook/flutterwave/', views.flutterwave_webhook, name='flutterwave_webhook'),
    path('success/<str:reference>/', views.payment_success, name='payment_success'),
    path('pending/<str:reference>/', views.payment_pending, name='payment_pending'),
    path('failed/<str:reference>/', views.payment_failed, name='payment_failed'),
]
