# orders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.views import get_cart # Import cart helper
from products.models import Product # To update product stock

@login_required # Only logged-in users can create orders
def order_create(request):
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user # Link order to authenticated user
            order.save()

            # Create order items from cart
            for product_id_str, item_data in cart.items():
                product = get_object_or_404(Product, id=int(product_id_str))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=float(item_data['price']),
                    quantity=item_data['quantity']
                )
                # Reduce product stock
                product.stock -= item_data['quantity']
                product.save()

            # Clear the cart
            del request.session['cart']
            request.session.modified = True

            messages.success(request, 'Order placed successfully! Redirecting to payment.')
            # Redirect to payment gateway
            return redirect('payments:process_payment', order_id=order.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        # Pre-fill form for logged-in users
        initial_data = {
            'first_name': request.user.first_name if request.user.first_name else '',
            'last_name': request.user.last_name if request.user.last_name else '',
            'email': request.user.email,
            # You might add address details if stored in user profile
        }
        form = OrderCreateForm(initial=initial_data)

    # Calculate cart total for display
    cart_products = []
    total_price = 0
    for product_id_str, item_data in cart.items():
        product = get_object_or_404(Product, id=int(product_id_str))
        quantity = item_data['quantity']
        price = float(item_data['price'])
        item_total = quantity * price
        total_price += item_total
        cart_products.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'item_total': item_total
        })

    context = {
        'form': form,
        'cart_products': cart_products,
        'total_price': total_price
    }
    return render(request, 'orders/order_create.html', context)

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    context = {
        'orders': orders
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order
    }
    return render(request, 'orders/order_detail.html', context)