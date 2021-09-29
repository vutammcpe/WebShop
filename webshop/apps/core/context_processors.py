from django.shortcuts import get_object_or_404
from .models import Product


def cart_contents(request):
    """
    Ensures that the cart contents are available when rendering
    every page
    """
    cart = request.session.get('apps', {})

    cart_items = []
    total = 0
    product_count = 0
    tong = 0

    for id, quantity in cart.items():
        product = get_object_or_404(Product, pk=id)
        total += quantity * product.price
        product_count += quantity
        cart_items.append({'id': id,
                           'quantity': quantity,
                           'product': product})

    return {'cart_items': cart_items, 'tong':tong,
            'total': total,
            'product_count': product_count}
