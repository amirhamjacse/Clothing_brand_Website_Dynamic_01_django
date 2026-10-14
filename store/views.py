from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from store.models import Category, Product, ProductVariant, Order, OrderItem, Coupon, Review
from store.cart import Cart

def switch_language(request, lang):
    if lang in ['bn', 'en']:
        request.session['lang'] = lang
        msg = 'ভাষা পরিবর্তিত হয়েছে: বাংলা' if lang == 'bn' else 'Language switched to English'
        messages.success(request, msg)
    referer = request.META.get('HTTP_REFERER') or '/'
    return redirect(referer)


def home(request):
    featured_categories = Category.objects.filter(is_featured=True).order_by('order')[:6]
    new_arrivals = Product.objects.filter(is_active=True, is_new=True).order_by('-created_at')[:8]
    eid_specials = Product.objects.filter(is_active=True, is_eid_special=True).order_by('-created_at')[:8]
    bestsellers = Product.objects.filter(is_active=True, is_bestseller=True).order_by('-created_at')[:8]
    recent_reviews = Review.objects.all().order_by('-created_at')[:6]
    hero_showcase_products = Product.objects.filter(is_active=True).order_by('-is_eid_special', '-is_bestseller', '-created_at')[:5]

    context = {
        'featured_categories': featured_categories,
        'new_arrivals': new_arrivals,
        'eid_specials': eid_specials,
        'bestsellers': bestsellers,
        'recent_reviews': recent_reviews,
        'hero_showcase_products': hero_showcase_products,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all().order_by('order')

    # Filtering
    category_slug = request.GET.get('category')
    gender = request.GET.get('gender')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', 'newest')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    if gender and gender in ['men', 'women', 'kids', 'unisex']:
        products = products.filter(gender=gender)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(fabric__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    if min_price:
        try:
            products = products.filter(regular_price__gte=Decimal(min_price))
        except Exception:
            pass

    if max_price:
        try:
            products = products.filter(regular_price__lte=Decimal(max_price))
        except Exception:
            pass

    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('regular_price')
    elif sort_by == 'price_high':
        products = products.order_by('-regular_price')
    elif sort_by == 'popular':
        products = products.order_by('-rating', '-rating_count')
    else:
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'selected_gender': gender,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_count': products.count(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variants = product.variants.all()
    gallery_images = product.gallery_images.all()
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    reviews = product.reviews.all().order_by('-created_at')

    # Available sizes & colors from variants
    sizes = list(dict.fromkeys([v.size for v in variants if v.size]))
    colors = list(dict.fromkeys([(v.color, v.color_code) for v in variants if v.color]))

    context = {
        'product': product,
        'variants': variants,
        'gallery_images': gallery_images,
        'related_products': related_products,
        'reviews': reviews,
        'sizes': sizes,
        'colors': colors,
    }
    return render(request, 'store/product_detail.html', context)


@require_POST
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    size = request.POST.get('size', 'Regular')
    color = request.POST.get('color', 'Default')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    cart.add(product=product, size=size, color=color, quantity=quantity)
    messages.success(request, f'Added "{product.name}" ({size}) to your bag!')

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'store:cart_detail'
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': len(cart),
            'cart_subtotal': str(cart.get_subtotal()),
            'message': f'"{product.name}" added to bag'
        })
    return redirect(next_url)


def cart_detail(request):
    cart = Cart(request)
    coupon_code = request.session.get('coupon_code', '')
    coupon_discount = Decimal(str(request.session.get('coupon_discount', 0)))
    subtotal = cart.get_subtotal()
    shipping = Decimal('60.00') if len(cart) > 0 else Decimal('0.00')
    grand_total = max(Decimal('0.00'), subtotal - coupon_discount + shipping)

    context = {
        'cart': cart,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'shipping': shipping,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def update_cart_item(request):
    cart = Cart(request)
    key = request.POST.get('key')
    quantity = request.POST.get('quantity')
    if key and quantity is not None:
        cart.update_quantity(key, quantity)
        messages.success(request, 'Shopping bag updated.')
    return redirect('store:cart_detail')


def remove_cart_item(request, key):
    cart = Cart(request)
    cart.remove(key)
    messages.info(request, 'Item removed from your bag.')
    return redirect('store:cart_detail')


@require_POST
def apply_coupon(request):
    code = request.POST.get('code', '').strip().upper()
    cart = Cart(request)
    subtotal = cart.get_subtotal()

    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
        if subtotal < coupon.min_spend:
            messages.error(request, f'Coupon requires minimum spend of ৳{coupon.min_spend}.')
        else:
            discount = (subtotal * coupon.discount_percent) / Decimal(100)
            if discount > coupon.max_discount:
                discount = coupon.max_discount
            request.session['coupon_code'] = coupon.code
            request.session['coupon_discount'] = float(discount)
            messages.success(request, f'Coupon "{coupon.code}" applied! You saved ৳{discount:.2f}.')
    except Coupon.DoesNotExist:
        messages.error(request, 'Invalid or expired promo code.')

    return redirect('store:cart_detail')


def remove_coupon(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'coupon_discount' in request.session:
        del request.session['coupon_discount']
    messages.info(request, 'Coupon removed.')
    return redirect('store:cart_detail')


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your shopping bag is empty. Please add items to checkout.')
        return redirect('store:product_list')

    subtotal = cart.get_subtotal()
    coupon_code = request.session.get('coupon_code', '')
    coupon_discount = Decimal(str(request.session.get('coupon_discount', 0)))

    # Prefill for logged in user
    initial_data = {}
    if request.user.is_authenticated:
        initial_data['full_name'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        initial_data['email'] = request.user.email
        if hasattr(request.user, 'profile'):
            initial_data['phone'] = request.user.profile.phone
            initial_data['division'] = request.user.profile.division
            initial_data['district'] = request.user.profile.district
            initial_data['address'] = request.user.profile.address

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        division = request.POST.get('division', 'Dhaka').strip()
        district = request.POST.get('district', 'Dhaka').strip()
        delivery_address = request.POST.get('delivery_address', '').strip()
        delivery_area = request.POST.get('delivery_area', 'inside_dhaka')
        payment_method = request.POST.get('payment_method', 'cod')
        sender_number = request.POST.get('sender_number', '').strip()
        trx_id = request.POST.get('trx_id', '').strip()
        customer_notes = request.POST.get('customer_notes', '').strip()

        if not full_name or not phone or not delivery_address:
            messages.error(request, 'Please provide your name, phone number, and delivery address.')
            return render(request, 'store/checkout.html', {'cart': cart, 'subtotal': subtotal, 'coupon_discount': coupon_discount})

        # Calculate shipping cost
        shipping_cost = Decimal('60.00') if delivery_area == 'inside_dhaka' else Decimal('120.00')
        total_amount = max(Decimal('0.00'), subtotal - coupon_discount + shipping_cost)

        # Payment status
        payment_status = 'unpaid'
        if payment_method in ['bkash', 'nagad', 'rocket'] and trx_id:
            payment_status = 'paid'

        # Create Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            phone=phone,
            email=email,
            division=division,
            district=district,
            delivery_address=delivery_address,
            delivery_area=delivery_area,
            shipping_cost=shipping_cost,
            subtotal=subtotal,
            discount_amount=coupon_discount,
            total_amount=total_amount,
            coupon_code=coupon_code,
            payment_method=payment_method,
            payment_status=payment_status,
            sender_number=sender_number,
            trx_id=trx_id,
            customer_notes=customer_notes,
            status='pending',
        )

        # Create Order Items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['name'],
                product_sku=item.get('sku', ''),
                size=item.get('size', ''),
                color=item.get('color', ''),
                price=item['unit_price'],
                quantity=item['quantity'],
                subtotal=item['total_price'],
            )
            # Reduce stock if product exists
            if item['product']:
                item['product'].stock = max(0, item['product'].stock - item['quantity'])
                item['product'].save()

        # Clear cart & coupon
        cart.clear()
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
        if 'coupon_discount' in request.session:
            del request.session['coupon_discount']

        messages.success(request, f'Alhamdulillah! Your order #{order.order_number} has been placed successfully.')
        return redirect('store:order_success', order_number=order.order_number)

    context = {
        'cart': cart,
        'subtotal': subtotal,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'initial_data': initial_data,
    }
    return render(request, 'store/checkout.html', context)


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'store/order_success.html', {'order': order})


def track_order(request):
    order = None
    searched = False
    order_number = request.GET.get('order_number', '').strip()
    phone = request.GET.get('phone', '').strip()

    if order_number and phone:
        searched = True
        try:
            order = Order.objects.get(
                Q(order_number__iexact=order_number),
                Q(phone__endswith=phone[-10:])
            )
        except Order.DoesNotExist:
            order = None

    context = {
        'order': order,
        'searched': searched,
        'order_number': order_number,
        'phone': phone,
    }
    return render(request, 'store/track_order.html', context)


@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    name = request.POST.get('name', 'Anonymous').strip()
    city = request.POST.get('city', 'Dhaka').strip()
    rating = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '').strip()

    if comment:
        Review.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            name=name,
            city=city,
            rating=rating,
            comment=comment,
        )
        messages.success(request, 'Thank you! Your review has been submitted.')
    return redirect('store:product_detail', slug=product.slug)
