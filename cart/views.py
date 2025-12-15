# cart/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from products.models import Product
from django.contrib import messages

# Helper function to get or create the cart in the session
def get_cart(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']

@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    product_id_str = str(product.id) # Session keys must be strings

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {
            'quantity': quantity,
            'price': str(product.price) # Store price as string to avoid serialization issues
        }

    # Ensure quantity doesn't exceed stock
    if cart[product_id_str]['quantity'] > product.stock:
        cart[product_id_str]['quantity'] = product.stock
        messages.warning(request, f'Only {product.stock} of {product.name} are available.')
    else:
        messages.success(request, f'{quantity} x {product.name} added to cart.')

    request.session.modified = True # Tell Django the session has been modified
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = get_cart(request)
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        messages.info(request, 'Item removed from cart.')
        request.session.modified = True
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart = get_cart(request)
    product_id_str = str(product_id)
    new_quantity = int(request.POST.get('quantity', 1))

    if product_id_str in cart:
        product = get_object_or_404(Product, id=product_id)
        if new_quantity > product.stock:
            new_quantity = product.stock
            messages.warning(request, f'Only {product.stock} of {product.name} are available. Quantity adjusted.')
        elif new_quantity <= 0:
            del cart[product_id_str]
            messages.info(request, 'Item removed from cart.')
        else:
            cart[product_id_str]['quantity'] = new_quantity
            messages.success(request, f'Quantity for {product.name} updated to {new_quantity}.')

        request.session.modified = True
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = get_cart(request)
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
        'cart_products': cart_products,
        'total_price': total_price
    }
    return render(request, 'cart/cart_detail.html', context)