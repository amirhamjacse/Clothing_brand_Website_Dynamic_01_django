from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.contrib.auth.decorators import user_passes_test
from django.utils.text import slugify
from store.models import Order, OrderItem, Product, Category, Coupon, ProductVariant

def is_admin_or_staff(user):
    # If not logged in, we allow dashboard access if configured for demo or redirect to staff login
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def dashboard_home(request):
    # Overall statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    confirmed_orders = Order.objects.filter(status='confirmed').count()
    processing_orders = Order.objects.filter(status='processing').count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    delivered_orders = Order.objects.filter(status='delivered').count()

    total_revenue = Order.objects.filter(~Q(status='cancelled')).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    pending_revenue = Order.objects.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')

    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lte=5, is_active=True).count()

    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    top_products = Product.objects.filter(is_active=True).order_by('-rating', '-stock')[:5]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'top_products': top_products,
    }
    return render(request, 'dashboard/index.html', context)


def order_list(request):
    status_filter = request.GET.get('status', '')
    payment_filter = request.GET.get('payment', '')
    search = request.GET.get('q', '').strip()

    orders = Order.objects.all().order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)
    if payment_filter:
        orders = orders.filter(payment_method=payment_filter)
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(full_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(trx_id__icontains=search)
        )

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'search': search,
        'status_choices': Order.STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_CHOICES,
    }
    return render(request, 'dashboard/orders.html', context)


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        payment_status = request.POST.get('payment_status')
        courier_tracking_id = request.POST.get('courier_tracking_id', '').strip()
        admin_notes = request.POST.get('admin_notes', '').strip()

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
        if payment_status in dict(Order.PAYMENT_STATUS_CHOICES):
            order.payment_status = payment_status
        order.courier_tracking_id = courier_tracking_id
        order.admin_notes = admin_notes
        order.save()
        messages.success(request, f"Order #{order.order_number} updated successfully.")
        return redirect('dashboard:order_detail', order_id=order.id)

    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'dashboard/order_detail.html', context)


def order_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'dashboard/order_invoice.html', {'order': order})


def product_management(request):
    category_id = request.GET.get('category')
    search = request.GET.get('q', '').strip()
    stock_filter = request.GET.get('stock')

    products = Product.objects.all().order_by('-created_at')

    if category_id:
        products = products.filter(category_id=category_id)
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(fabric__icontains=search)
        )
    if stock_filter == 'low':
        products = products.filter(stock__lte=5)
    elif stock_filter == 'out':
        products = products.filter(stock=0)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'category_id': category_id,
        'search': search,
        'stock_filter': stock_filter,
    }
    return render(request, 'dashboard/products.html', context)


def product_add(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category')
        gender = request.POST.get('gender', 'men')
        fabric = request.POST.get('fabric', '100% Combed Cotton')
        sku = request.POST.get('sku', '').strip()
        regular_price = Decimal(request.POST.get('regular_price', '0'))
        discount_price_raw = request.POST.get('discount_price', '').strip()
        discount_price = Decimal(discount_price_raw) if discount_price_raw else None
        stock = int(request.POST.get('stock', 20))
        description = request.POST.get('description', '')
        features = request.POST.get('features', '')
        primary_image = request.POST.get('primary_image', '').strip()
        hover_image = request.POST.get('hover_image', '').strip()

        is_featured = bool(request.POST.get('is_featured'))
        is_new = bool(request.POST.get('is_new'))
        is_bestseller = bool(request.POST.get('is_bestseller'))
        is_eid_special = bool(request.POST.get('is_eid_special'))
        is_active = bool(request.POST.get('is_active', True))

        if not sku:
            sku = f"AHMZ-{name[:3].upper()}-{Product.objects.count() + 1:04d}"

        if not primary_image:
            primary_image = "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&auto=format&fit=crop&q=80"

        category = get_object_or_404(Category, id=category_id)

        product = Product.objects.create(
            name=name,
            sku=sku,
            category=category,
            gender=gender,
            fabric=fabric,
            description=description,
            features=features,
            regular_price=regular_price,
            discount_price=discount_price,
            stock=stock,
            primary_image=primary_image,
            hover_image=hover_image,
            is_featured=is_featured,
            is_new=is_new,
            is_bestseller=is_bestseller,
            is_eid_special=is_eid_special,
            is_active=is_active,
        )

        # Create standard variants (Sizes 38, 40, 42, 44 or S, M, L, XL)
        sizes_input = request.POST.get('sizes', '38, 40, 42, 44')
        sizes = [s.strip() for s in sizes_input.split(',') if s.strip()]
        for s in sizes:
            ProductVariant.objects.create(
                product=product,
                size=s,
                color='Default',
                stock=stock // len(sizes) if len(sizes) > 0 else stock
            )

        messages.success(request, f'Product "{product.name}" created successfully!')
        return redirect('dashboard:product_management')

    return render(request, 'dashboard/product_form.html', {'categories': categories, 'action': 'Add'})


def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.category_id = request.POST.get('category')
        product.gender = request.POST.get('gender', 'men')
        product.fabric = request.POST.get('fabric', product.fabric)
        product.sku = request.POST.get('sku', product.sku).strip()
        product.regular_price = Decimal(request.POST.get('regular_price', str(product.regular_price)))
        discount_price_raw = request.POST.get('discount_price', '').strip()
        product.discount_price = Decimal(discount_price_raw) if discount_price_raw else None
        product.stock = int(request.POST.get('stock', product.stock))
        product.description = request.POST.get('description', '')
        product.features = request.POST.get('features', '')
        
        img = request.POST.get('primary_image', '').strip()
        if img:
            product.primary_image = img
        product.hover_image = request.POST.get('hover_image', '').strip()

        product.is_featured = bool(request.POST.get('is_featured'))
        product.is_new = bool(request.POST.get('is_new'))
        product.is_bestseller = bool(request.POST.get('is_bestseller'))
        product.is_eid_special = bool(request.POST.get('is_eid_special'))
        product.is_active = bool(request.POST.get('is_active'))
        product.save()

        messages.success(request, f'Product "{product.name}" updated successfully!')
        return redirect('dashboard:product_management')

    return render(request, 'dashboard/product_form.html', {
        'product': product,
        'categories': categories,
        'action': 'Edit'
    })


def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    name = product.name
    product.delete()
    messages.warning(request, f'Product "{name}" has been deleted.')
    return redirect('dashboard:product_management')


def category_management(request):
    categories = Category.objects.all().order_by('order')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        gender = request.POST.get('gender', 'all')
        description = request.POST.get('description', '').strip()
        image = request.POST.get('image', '').strip()

        if name:
            Category.objects.create(
                name=name,
                gender=gender,
                description=description,
                image=image,
                is_featured=True,
            )
            messages.success(request, f'Category "{name}" added!')
            return redirect('dashboard:category_management')

    return render(request, 'dashboard/categories.html', {'categories': categories})


def coupon_management(request):
    coupons = Coupon.objects.all().order_by('-id')
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        discount_percent = int(request.POST.get('discount_percent', 10))
        min_spend = Decimal(request.POST.get('min_spend', '1000'))
        max_discount = Decimal(request.POST.get('max_discount', '500'))

        if code:
            Coupon.objects.create(
                code=code,
                discount_percent=discount_percent,
                min_spend=min_spend,
                max_discount=max_discount,
                is_active=True,
            )
            messages.success(request, f'Coupon "{code}" created!')
            return redirect('dashboard:coupon_management')

    return render(request, 'dashboard/coupons.html', {'coupons': coupons})
