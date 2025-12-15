# payments/urls.py

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('direct-success/<int:order_id>/', views.direct_payment_success, name='direct_payment_success'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'), # Stripe webhook endpoint
]