# payments/views.py

import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt # For webhook
from orders.models import Order
from django.contrib import messages

# Configure Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, paid=False)

    if request.method == 'POST':
        # For direct payment success (bypassing Stripe redirect)
        # Mark order as paid immediately (for demo/testing purposes)
        order.paid = True
        order.status = 'processing'
        order.stripe_id = 'direct_payment_' + str(order.id)
        order.save()
        
        messages.success(request, f'Payment successful for Order #{order.id}!')
        return redirect('payments:direct_payment_success', order_id=order.id)
    
    # If GET request, just display the payment page
    context = {
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'payments/process_payment.html', context)

def payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                order_id = session.metadata.get('order_id')
                if order_id:
                    order = get_object_or_404(Order, id=int(order_id))
                    order.paid = True
                    order.status = 'processing' # Update status after payment
                    order.save()
                    messages.success(request, f'Payment successful for Order #{order.id}!')
                    return render(request, 'payments/payment_success.html', {'order': order})
            else:
                messages.error(request, 'Payment was not successful. Please try again.')
        except stripe.error.StripeError as e:
            messages.error(request, f'Stripe error: {e}')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {e}')
    else:
        messages.error(request, 'Payment session ID not found.')
    return redirect('products:product_list') # Fallback


def payment_cancel(request):
    messages.info(request, 'Payment cancelled. Your order has not been placed.')
    return render(request, 'payments/payment_cancel.html')


def direct_payment_success(request, order_id):
    """Direct payment success page - bypasses Stripe redirect"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Ensure the order is marked as paid (in case it wasn't already)
        if not order.paid:
            order.paid = True
            order.status = 'processing'
            order.stripe_id = 'direct_payment_' + str(order.id)
            order.save()
        
        context = {
            'order': order
        }
        return render(request, 'payments/direct_payment_success.html', context)
    except Exception as e:
        # Log the error and return a proper response
        messages.error(request, f'Error loading payment success page: {str(e)}')
        return redirect('products:product_list')


@csrf_exempt # Disable CSRF token for this view as Stripe sends POST requests
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.metadata.get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=int(order_id))
                if not order.paid: # Prevent double processing
                    order.paid = True
                    order.status = 'processing'
                    order.stripe_id = session.id # Ensure stripe_id is stored
                    order.save()
                    # You might send a confirmation email here
                    print(f"Order {order.id} marked as paid and processing via webhook.")
            except Order.DoesNotExist:
                print(f"Order with ID {order_id} not found for webhook.")
        else:
            print("Order ID not found in checkout.session.completed metadata.")
    elif event['type'] == 'payment_intent.succeeded':
        # Handle payment_intent.succeeded
        payment_intent = event['data']['object']
        # This event can also be used, but checkout.session.completed is often preferred for Checkout flow
        print(f"PaymentIntent {payment_intent.id} succeeded.")
    # Add other event types as needed

    return HttpResponse(status=200)