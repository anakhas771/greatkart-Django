from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from store.models import Product, Variation
from .models import Wishlist

# --------------------------
# Add product to wishlist
# --------------------------
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    # Save selected variations
    selected_variations = []
    for key, value in request.POST.items():
        if key in ['color', 'size']:  # adjust according to your variation categories
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                selected_variations.append(variation)
            except Variation.DoesNotExist:
                continue

    if selected_variations:
        wishlist_item.variations.set(selected_variations)
        wishlist_item.save()

    return redirect('wishlist')


# --------------------------
# Remove from wishlist
# --------------------------
@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('wishlist')


# --------------------------
# Display wishlist
# --------------------------
@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist/wishlist.html', {'items': items})
