# products/views.py

from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True) # Only show available products

    if category_slug:
        # If a category slug is provided, filter products by that category
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, 'products/product_list.html', context)

def product_list_by_category(request, category_slug):
    """Display products filtered by a specific category."""
    category = get_object_or_404(Category, slug=category_slug)
    categories = Category.objects.all()
    products = Product.objects.filter(category=category, available=True)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, id, slug):
    # Retrieve a single product by its ID and slug for uniqueness
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    context = {
        'product': product
    }
    return render(request, 'products/product_detail.html', context)
