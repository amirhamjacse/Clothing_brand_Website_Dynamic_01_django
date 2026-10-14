from decimal import Decimal
from store.cart import Cart
from store.models import Category
from store.translations import get_translation_dict

def cart_context(request):
    cart = Cart(request)
    nav_categories = Category.objects.all().order_by('order')[:8]
    
    # Language preference (default is 'bn')
    current_lang = request.session.get('lang', 'bn')
    if current_lang not in ['bn', 'en']:
        current_lang = 'bn'

    t_dict = get_translation_dict(current_lang)

    # Calculate discount if coupon applied
    coupon_code = request.session.get('coupon_code')
    coupon_discount = request.session.get('coupon_discount', 0)
    subtotal = cart.get_subtotal()
    discount_amount = Decimal(str(coupon_discount))

    # Shipping default inside dhaka
    shipping_cost = Decimal('60.00') if len(cart) > 0 else Decimal('0.00')
    total = max(Decimal('0.00'), subtotal - discount_amount + shipping_cost)

    return {
        'cart': cart,
        'cart_count': len(cart),
        'cart_subtotal': subtotal,
        'cart_items': cart.get_items_list(),
        'nav_categories': nav_categories,
        'coupon_code': coupon_code,
        'coupon_discount': discount_amount,
        'cart_total_estimate': total,
        'CURRENT_LANG': current_lang,
        'T': t_dict,
        'BRAND_NAME': 'AHMZ',
        'BRAND_FULL_NAME': 'AHMZ Artisan Lifestyle',
        'HOTLINE': '+880 1812-345678',
        'HOTLINE_CLEAN': '8801812345678',
        'OFFICE_ADDRESS': 'House 42, Road 11, Block D, Banani, Dhaka-1213, Bangladesh',
    }
