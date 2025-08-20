from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Variation
from .models import Cart, CartItem

# --------------------------
# Helper function to get session cart id
# --------------------------
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# --------------------------
# Add product to cart
# --------------------------
def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variation = []

    # Handle variations from POST
    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                continue

    # Determine if user is authenticated or not
    if request.user.is_authenticated:
        user = request.user
        cart = None
    else:
        user = None
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))

    # Get cart items
    if user:
        cart_items = CartItem.objects.filter(product=product, user=user)
    else:
        cart_items = CartItem.objects.filter(product=product, cart=cart)

    # Compare existing variations
    existing_variations_list = []
    item_ids = []
    for item in cart_items:
        existing_variations_list.append(list(item.variations.all()))
        item_ids.append(item.id)

    if product_variation in existing_variations_list:
        # Variation exists, increment quantity
        index = existing_variations_list.index(product_variation)
        cart_item = CartItem.objects.get(id=item_ids[index])
        cart_item.quantity += 1
        cart_item.save()
    else:
        # Create new cart item
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            user=user,
            cart=None if user else cart
        )
        if product_variation:
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')

# --------------------------
# Remove 1 quantity from cart item
# --------------------------
def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except ObjectDoesNotExist:
        pass

    return redirect('cart')

# --------------------------
# Remove entire cart item
# --------------------------
def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except ObjectDoesNotExist:
        pass

    return redirect('cart')

# --------------------------
# Display cart
# --------------------------
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

# --------------------------
# Checkout (login required)
# --------------------------
@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)

        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
