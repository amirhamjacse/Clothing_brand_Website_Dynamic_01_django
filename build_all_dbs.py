import os
import shutil
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from store.models import Category, Product, ProductVariant, Coupon, Order, OrderItem, Review
from accounts.models import UserProfile

BASE_DIR = settings.BASE_DIR

# Common Setup Helpers
def create_common_data():
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@ahmz-lifestyle.com', 'admin123')
        admin_user.first_name = "AHMZ"
        admin_user.last_name = "Admin"
        admin_user.save()
        profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        profile.phone = "01812345678"
        profile.district = "Dhaka"
        profile.address = "House 42, Road 11, Block D, Banani, Dhaka"
        profile.save()

    Coupon.objects.get_or_create(
        code='EID2026',
        defaults={
            'discount_percent': 10,
            'min_spend': Decimal('1500.00'),
            'max_discount': Decimal('500.00'),
            'is_active': True
        }
    )
    Coupon.objects.get_or_create(
        code='AHMZ15',
        defaults={
            'discount_percent': 15,
            'min_spend': Decimal('3000.00'),
            'max_discount': Decimal('1000.00'),
            'is_active': True
        }
    )

def seed_products(cats, products_data):
    for idx, p_info in enumerate(products_data, start=1):
        sizes = p_info.pop('sizes', ['Regular'])
        sku_seed = f"AHMZ-{p_info['category'].name[:3].upper()}-{idx:04d}"
        while Product.objects.filter(sku=sku_seed).exists():
            sku_seed = f"AHMZ-{p_info['category'].name[:3].upper()}-{Product.objects.count() + idx + 10:04d}"
        
        prod = Product.objects.create(
            sku=sku_seed,
            **p_info
        )
        for s in sizes:
            ProductVariant.objects.create(
                product=prod,
                size=s,
                color='Default',
                stock=max(5, prod.stock // len(sizes) if len(sizes) > 0 else prod.stock)
            )

def seed_sample_orders(first_product, second_product):
    p1_price = first_product.get_price()
    p2_price = second_product.get_price()

    o1 = Order.objects.create(
        order_number='AHMZ-54210',
        full_name='রাশেদ জামান',
        phone='01711223344',
        email='rashed@gmail.com',
        division='Dhaka',
        district='Dhaka',
        delivery_address='হাউজ নং ১৫, রোড নং ৪, সেক্টর ৩, উত্তরা, ঢাকা',
        delivery_area='inside_dhaka',
        shipping_cost=Decimal('60.00'),
        subtotal=p1_price,
        discount_amount=Decimal('200.00'),
        total_amount=p1_price - Decimal('200.00') + Decimal('60.00'),
        coupon_code='EID2026',
        payment_method='cod',
        payment_status='paid',
        status='delivered',
        courier_tracking_id='PATHAO-DK-9082',
        admin_notes='ডেলিভারি সম্পন্ন হয়েছে এবং টাকা রিসিভড।'
    )
    OrderItem.objects.create(
        order=o1, product=first_product, product_name=first_product.name,
        product_sku=first_product.sku, size=first_product.variants.first().size if first_product.variants.exists() else 'Regular',
        price=p1_price, quantity=1, subtotal=p1_price
    )

    o2 = Order.objects.create(
        order_number='AHMZ-68341',
        full_name='আসিফ মাহমুদ',
        phone='01819887766',
        email='asif.ctg@yahoo.com',
        division='Chittagong',
        district='Chittagong',
        delivery_address='ফ্ল্যাট ৪বি, মেঘনা হাইটস, নাসিরাবাদ, চট্টগ্রাম',
        delivery_area='outside_dhaka',
        shipping_cost=Decimal('120.00'),
        subtotal=p2_price,
        discount_amount=Decimal('0.00'),
        total_amount=p2_price + Decimal('120.00'),
        payment_method='bkash',
        payment_status='paid',
        sender_number='01819887766',
        trx_id='BK98A2L41Z',
        status='shipped',
        courier_tracking_id='ST-CTG-44910',
        admin_notes='বিকাশ পেমেন্ট ভেরিফাইড। স্টিডফাস্ট কুরিয়ারে বুকিং সম্পন্ন।'
    )
    OrderItem.objects.create(
        order=o2, product=second_product, product_name=second_product.name,
        product_sku=second_product.sku, size=second_product.variants.first().size if second_product.variants.exists() else 'Regular',
        price=p2_price, quantity=1, subtotal=p2_price
    )


# ================= DATA DEFINITIONS =================

CLOTHING_CATEGORIES = [
    {
        'name': 'পাঞ্জাবি ও কাবলি (Panjabi & Kabli)',
        'slug': 'panjabi-kabli',
        'gender': 'men',
        'image': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&auto=format&fit=crop&q=80',
        'description': 'খাঁটি মিশরীয় গিজা কটন, সুতি জ্যাকার্ড ও ঐতিহ্যবাহী এমব্রয়ডারি করা পাঞ্জাবি কালেকশন।',
        'order': 1
    },
    {
        'name': 'জামদানি ও এক্সক্লুসিভ শাড়ি (Saree)',
        'slug': 'jamdani-saree',
        'gender': 'women',
        'image': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80',
        'description': 'ঐতিহ্যবাহী ঢাকাই জামদানি, মসলিন সিল্ক ও কাঞ্চিপুরম ডিজাইনার শাড়ি।',
        'order': 2
    },
    {
        'name': 'সালোয়ার কামিজ ও কুর্তি (Salwar & Kurti)',
        'slug': 'salwar-kurti',
        'gender': 'women',
        'image': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80',
        'description': 'আধুনিক তরুণীদের জন্য আরামদায়ক লিনেন কুর্তি ও থ্রি-পিস সেট।',
        'order': 3
    },
    {
        'name': 'ক্যাজুয়াল পোলো ও প্রিমিয়াম টি-শার্ট',
        'slug': 'polo-tshirt',
        'gender': 'unisex',
        'image': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80',
        'description': '২২০ জিএসএম ভারী সুতি পোলো শার্ট ও প্রিমিয়াম ড্রপ-শোল্ডার টি-শার্ট।',
        'order': 4
    },
]

CLOTHING_PRODUCTS = [
    {
        'name': 'রয়্যাল এমব্রয়ডারি জ্যাকার্ড পাঞ্জাবি - ডিপ নেভি ব্লু',
        'cat_slug': 'panjabi-kabli',
        'gender': 'men',
        'fabric': '100% Fine Combed Jacquard Cotton',
        'description': 'আভিজাত্য ও ঐতিহ্যের অপরূপ সমন্বয়। নেকলাইনে নিখুঁত কারুকাজ ও প্রিমিয়াম মেটালিক বোতাম সহ আকর্ষণীয় ডিপ নেভি ব্লু পাঞ্জাবি।',
        'features': 'মান্দারিন কলার ও থ্রেড এমব্রয়ডারি নকশা\nউচ্চমানের অ্যান্টি-রিঙ্কেল সুতি ফেব্রিক\nদুই পাশে পকেট ও ডাবল স্টিচিং',
        'regular_price': Decimal('2950.00'),
        'discount_price': Decimal('2450.00'),
        'primary_image': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&auto=format&fit=crop&q=80',
        'hover_image': 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&auto=format&fit=crop&q=80',
        'stock': 28,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.9'),
        'rating_count': 34,
        'sizes': ['38', '40', '42', '44', '46']
    },
    {
        'name': 'আইভরি হোয়াইট গিজা কটন পাঞ্জাবি - ক্লাসিক ঢাকা ড্রপ',
        'cat_slug': 'panjabi-kabli',
        'gender': 'men',
        'fabric': '100% Pure Egyptian Giza Cotton',
        'description': 'সাদা রঙের চিরন্তন স্নিগ্ধতা। গ্রীষ্মের তীব্র রোদ কিংবা ঈদের সকালের নামাজ—১০০% গিজা কটনের এই পাঞ্জাবি আপনার ব্যক্তিত্বকে দেবে রাজকীয় রূপ।',
        'features': 'সফট কটন ফিনিশিং যা সারাদিন শীতল অনুভূতি দেয়\nহাতে বসানো স্ফটিক বোতাম\nসেমি-ফিটেড আরামদায়ক কাটিং',
        'regular_price': Decimal('2600.00'),
        'discount_price': Decimal('2190.00'),
        'primary_image': 'https://images.unsplash.com/photo-1621072156002-e2fccdc0b176?w=800&auto=format&fit=crop&q=80',
        'hover_image': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&auto=format&fit=crop&q=80',
        'stock': 18,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': False,
        'rating': Decimal('4.8'),
        'rating_count': 29,
        'sizes': ['38', '40', '42', '44']
    },
    {
        'name': 'ঐতিহ্যবাহী ঢাকাই জামদানি শাড়ি - রয়েল গোল্ডেন জারি',
        'cat_slug': 'jamdani-saree',
        'gender': 'women',
        'fabric': '100% Handwoven Muslin & Cotton Jamdani',
        'description': 'রূপগঞ্জের তাঁতিদের হাতে বোনা খাঁটি ঢাকাই জামদানি। সূক্ষ্ম গোল্ডেন জরি ও সুতার বুননে তৈরি এই শাড়ি প্রতিটি নারীর আভিজাত্যের প্রতীক।',
        'features': 'সম্পূর্ণ হস্তনির্মিত তাঁতের জামদানি বুনন\nউজ্জ্বল ও দীর্ঘস্থায়ী নকশা\nদৈর্ঘ্য: ১২ হাত (ব্লাউজ পিস সহ)',
        'regular_price': Decimal('5500.00'),
        'discount_price': Decimal('4750.00'),
        'primary_image': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 12,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('5.0'),
        'rating_count': 42,
        'sizes': ['Free Size']
    },
    {
        'name': 'ডিজাইনার লিনেন ফেস্টিভ কুর্তি - স্কাই ব্লু',
        'cat_slug': 'salwar-kurti',
        'gender': 'women',
        'fabric': 'Organic Breathable Linen',
        'description': 'গরমে সর্বোচ্চ স্বস্তি ও আধুনিক স্টাইল একসাথে। স্কাই ব্লু লিনেন ফ্যাব্রিকে সূক্ষ্ম প্যাচওয়ার্ক ও ফ্রন্ট বাটন ডিটেইলিং।',
        'features': 'ব্রিদেবল লিনেন যা ঘাম শোষণ করে\nA-লাইন কাটিং ও সাইড স্লিট\nথ্রি-কোয়ার্টার হাতা',
        'regular_price': Decimal('1850.00'),
        'discount_price': Decimal('1490.00'),
        'primary_image': 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 20,
        'is_eid_special': False,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.8'),
        'rating_count': 19,
        'sizes': ['S', 'M', 'L', 'XL']
    },
    {
        'name': 'সিগনেচার পিক পোলো শার্ট - ফরেস্ট গ্রিন',
        'cat_slug': 'polo-tshirt',
        'gender': 'unisex',
        'fabric': '220 GSM 100% Combed Pique Cotton',
        'description': 'আন্তর্জাতিক মানের ২২০ জিএসএম পিক কটন পোলো। কোনো লিন্ট উঠবে না ও বারবার ধোয়ার পরেও কলার ঢিলে হবে না।',
        'features': 'ডাবল রাইস পিক নিটিং\nস্ট্রং কলার ও ২-বাটন প্লাকেট\nএনজাইম ওয়াশড আল্ট্রা-সফট ফিনিশ',
        'regular_price': Decimal('1250.00'),
        'discount_price': Decimal('950.00'),
        'primary_image': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 35,
        'is_eid_special': False,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.9'),
        'rating_count': 55,
        'sizes': ['M', 'L', 'XL', 'XXL']
    },
]

SHOES_CATEGORIES = [
    {
        'name': 'প্রিমিয়াম লেদার লোফার (Loafers)',
        'slug': 'leather-loafers',
        'gender': 'men',
        'image': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800&auto=format&fit=crop&q=80',
        'description': '১০০% অরিজিনাল কাফ লেদার টাসেল ও পেনি লোফার। সারাদিনের সর্বোচ্চ আরাম ও রাজকীয় স্টাইল।',
        'order': 1
    },
    {
        'name': 'ক্লাসিক ফরমাল অক্সফোর্ড শু',
        'slug': 'formal-oxford',
        'gender': 'men',
        'image': 'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800&auto=format&fit=crop&q=80',
        'description': 'হ্যান্ডক্রাফটেড চামড়ার সোল সহ অফিস ও বিয়ের অনুষ্ঠানের জন্য প্রিমিয়াম ডার্বি ও অক্সফোর্ড জুতো।',
        'order': 2
    },
    {
        'name': 'হ্যান্ডক্রাফটেড স্নিকার্স ও ক্যাজুয়াল শু',
        'slug': 'casual-sneakers',
        'gender': 'unisex',
        'image': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80',
        'description': 'দৈনন্দিন হাঁটাচলা ও স্ট্রিট ফ্যাশনের জন্য আরামদায়ক লাইটওয়েট কুশন স্নিকার্স।',
        'order': 3
    },
]

SHOES_PRODUCTS = [
    {
        'name': 'হ্যান্ডক্রাফটেড প্রিমিয়াম টাসেল লোফার - ব্ল্যাক গ্লসি লেদার',
        'cat_slug': 'leather-loafers',
        'gender': 'men',
        'fabric': '100% Genuine Full-Grain Cow Leather',
        'description': 'খাঁটি লেদারের নিখুঁত কারুকার্য। নরম মেমোরি ফোম ইনসোল যা সারাদিন পরে থাকলেও পায়ে কোনো ক্লান্তি আনে না।',
        'features': 'ফুল-গ্রেইন প্রিমিয়াম লেদার আপার\nহস্তনির্মিত মার্জিত টাসেল ডিজাইন\nনন-স্লিপ অ্যান্টি-স্কিড রাবার সোল',
        'regular_price': Decimal('3850.00'),
        'discount_price': Decimal('3250.00'),
        'primary_image': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800&auto=format&fit=crop&q=80',
        'hover_image': 'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800&auto=format&fit=crop&q=80',
        'stock': 24,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.9'),
        'rating_count': 41,
        'sizes': ['39', '40', '41', '42', '43', '44']
    },
    {
        'name': 'ক্যাপ-টো ক্লাসিক অক্সফোর্ড ফরমাল শু - কগনাক ব্রাউন',
        'cat_slug': 'formal-oxford',
        'gender': 'men',
        'fabric': 'Imported Italian Calf Leather',
        'description': 'অভিজাত অফিসের মিটিং কিংবা বিয়েতে সেরা লুক দিতে কগনাক ব্রাউন কালারের অরিজিনাল লেদার অক্সফোর্ড শু।',
        'features': 'গুডিয়ার ওয়েল্টেড স্টাইল স্টিচিং\nক্যাপ-টো মার্জিত ফরমাল লুক\nসফট অর্থোপেডিক কুশন সাপোর্ট',
        'regular_price': Decimal('4200.00'),
        'discount_price': Decimal('3590.00'),
        'primary_image': 'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 16,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': False,
        'rating': Decimal('5.0'),
        'rating_count': 32,
        'sizes': ['39', '40', '41', '42', '43']
    },
    {
        'name': 'মিনিমালিস্ট আরবান লেদার স্নিকার্স - পিওর হোয়াইট',
        'cat_slug': 'casual-sneakers',
        'gender': 'unisex',
        'fabric': 'Premium Nappa Leather & Rubber Sole',
        'description': 'আধুনিক তরুণদের প্রথম পছন্দ অল-হোয়াইট প্রিমিয়াম লেদার স্নিকার্স। সহজে পরিষ্কারযোগ্য ও আল্ট্রা-লাইটওয়েট।',
        'features': 'ওয়াটার ও ডাস্ট রেসিস্ট্যান্ট নাপ্পা লেদার\nলাইটওয়েট শক-অ্যাবজরবিং সোল\nপ্যাডেড কলার ও হিল সাপোর্ট',
        'regular_price': Decimal('2750.00'),
        'discount_price': Decimal('2290.00'),
        'primary_image': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 30,
        'is_eid_special': False,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.8'),
        'rating_count': 67,
        'sizes': ['39', '40', '41', '42', '43', '44']
    },
]

WATCHES_CATEGORIES = [
    {
        'name': 'রয়্যাল ক্রোনোগ্রাফ মেটালিক ওয়াচ',
        'slug': 'chronograph-watches',
        'gender': 'men',
        'image': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&auto=format&fit=crop&q=80',
        'description': 'স্টেইনলেস স্টিল চেইন, স্যাফায়ার ক্রিস্টাল গ্লাস ও ৫ বার ওয়াটার রেসিস্ট্যান্ট ক্রোনোগ্রাফ।',
        'order': 1
    },
    {
        'name': 'প্রিমিয়াম লেদার অটোমেটিক ওয়াচ',
        'slug': 'automatic-leather-watches',
        'gender': 'unisex',
        'image': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800&auto=format&fit=crop&q=80',
        'description': 'কোনো ব্যাটারি ছাড়াই হাতের মোশনে চলা মেকানিক্যাল অটোমেটিক স্কেলিটন ঘড়ি।',
        'order': 2
    },
    {
        'name': 'অ্যামোলেড ডিসপ্লে স্মার্টওয়াচ প্রো',
        'slug': 'smartwatches',
        'gender': 'unisex',
        'image': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&auto=format&fit=crop&q=80',
        'description': 'ব্লুটুথ কলিং, হার্ট-রেট ও রক্তে অক্সিজেন মনিটর সহ প্রিমিয়াম AMOLED স্মার্টওয়াচ।',
        'order': 3
    },
]

WATCHES_PRODUCTS = [
    {
        'name': 'রয়্যাল ক্রোনোগ্রাফ স্টেইনলেস স্টিল ওয়াচ - এমারেল্ড গ্রিন ডায়াল',
        'cat_slug': 'chronograph-watches',
        'gender': 'men',
        'fabric': '316L Solid Stainless Steel & Sapphire Glass',
        'description': 'সময়ের নিখুঁত রাজকীয় প্রকাশ। এমারেল্ড গ্রিন সানবার্স্ট ডায়াল, থ্রি-সাবডায়াল স্টপওয়াচ ফাংশন ও স্ক্র্যাচ-প্রুফ স্যাফায়ার ক্রিস্টাল গ্লাস।',
        'features': '৩১৬এল মেডিকেল-গ্রেড স্টেইনলেস স্টিল চেইন\n৫০ মিটার (5 ATM) ওয়াটার রেসিস্ট্যান্স\nলুমিনাস হাত ও মার্কার যা অন্ধকারে জ্বলে\n১ বছরের অফিসিয়াল রিপ্লেসমেন্ট ওয়ারেন্টি',
        'regular_price': Decimal('4950.00'),
        'discount_price': Decimal('3990.00'),
        'primary_image': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&auto=format&fit=crop&q=80',
        'hover_image': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&auto=format&fit=crop&q=80',
        'stock': 15,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('5.0'),
        'rating_count': 48,
        'sizes': ['Standard Adjustable Steel']
    },
    {
        'name': 'মাস্টার অটোমেটিক মেকানিক্যাল স্কেলিটন ওয়াচ - রিচ ব্রাউন লেদার',
        'cat_slug': 'automatic-leather-watches',
        'gender': 'men',
        'fabric': 'Self-Winding Mechanical Movement & Italian Leather',
        'description': 'কোনো ব্যাটারির প্রয়োজন নেই, হাতের স্বাভাবিক মুভমেন্টেই স্বয়ংক্রিয়ভাবে চলবে। ডায়ালের উন্মুক্ত গিয়ারবক্স ঘড়িটিকে অনন্য শিল্পের রূপ দেয়।',
        'features': 'অটোমেটিক সেলফ-উইন্ডিং জাপানিজ মুভমেন্ট\nস্বচ্ছ স্কেলিটন কেস-ব্যাক\nখাঁটি স্টিচড জেনুইন লেদার স্ট্র্যাপ\nপ্রিমিয়াম গিফট বক্স অন্তর্ভুক্ত',
        'regular_price': Decimal('6200.00'),
        'discount_price': Decimal('4950.00'),
        'primary_image': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 10,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': False,
        'rating': Decimal('4.9'),
        'rating_count': 35,
        'sizes': ['Genuine Leather Strap']
    },
    {
        'name': 'আল্ট্রা AMOLED ব্লুটুথ কলিং স্মার্টওয়াচ - ম্যাট ব্ল্যাক',
        'cat_slug': 'smartwatches',
        'gender': 'unisex',
        'fabric': 'Aerospace Zinc Alloy Case & Silicone/Metal Strap',
        'description': '১.৪৩ ইঞ্চি উজ্জ্বল সুপার অ্যামোলেড অলওয়েজ-অন ডিসপ্লে। সরাসরি ঘড়ি থেকে কথা বলার জন্য ক্রিস্টাল ক্লিয়ার স্পিকার ও মাইক।',
        'features': 'হাই-ডেফিনিশন ব্লুটুথ কলিং ও কন্টাক্ট সিন্ক\nহার্ট রেট, রক্তচাপ ও স্লিপ ট্র্যাকার\n১০০+ স্পোর্টস মোড ও ক্যালোরি কাউন্টার\nআইপি৬৮ ওয়াটার রেটিং',
        'regular_price': Decimal('3650.00'),
        'discount_price': Decimal('2890.00'),
        'primary_image': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 25,
        'is_eid_special': False,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.8'),
        'rating_count': 59,
        'sizes': ['Dual Strap Included (Silicone + Metal)']
    },
]

COSMETICS_CATEGORIES = [
    {
        'name': 'স্কিনকেয়ার ও ব্রাইটনিং সিরাম',
        'slug': 'skincare-serums',
        'gender': 'unisex',
        'image': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&auto=format&fit=crop&q=80',
        'description': 'ডার্মাটোলজিস্ট টেস্টেড অর্গানিক ভিটামিন-সি, হায়ালুরোনিক অ্যাসিড ও নিয়াসিনামাইড ফেস সিরাম।',
        'order': 1
    },
    {
        'name': 'লিপস্টিক ও ফেস মেকআপ কালেকশন',
        'slug': 'lipsticks-makeup',
        'gender': 'women',
        'image': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800&auto=format&fit=crop&q=80',
        'description': '১২ ঘণ্টা স্থায়ী ওয়াটারপ্রুফ ভেলভেট ম্যাট লিপস্টিক, ব্লাশ ও ফাউন্ডেশন কম্বো।',
        'order': 2
    },
    {
        'name': 'লাক্সারি অ্যারোমা পারফিউম ও আতর',
        'slug': 'luxury-perfumes',
        'gender': 'unisex',
        'image': 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800&auto=format&fit=crop&q=80',
        'description': 'খাঁটি ফরাসি সুবাস ও অউদ নোটের লং-লাস্টিং প্রিমিয়াম পারফিউম। ২৪ ঘণ্টা স্থায়ী ফ্র্যাগ্রেন্স।',
        'order': 3
    },
]

COSMETICS_PRODUCTS = [
    {
        'name': 'পিওর ভিটামিন-সি ২০% ব্রাইটনিং ফেস সিরাম (30ml)',
        'cat_slug': 'skincare-serums',
        'gender': 'unisex',
        'fabric': 'Organic Botanical Extracts & 20% L-Ascorbic Acid',
        'description': 'ত্বকের দাগ দূর করতে ও প্রাকৃতিক উজ্জ্বলতা ফিরিয়ে আনতে ১০০% খাঁটি ভিটামিন-সি সিরাম। হায়ালুরোনিক অ্যাসিড ও ভিটামিন ই সমৃদ্ধ।',
        'features': 'ত্বকের মেছতা ও রোদে পোড়া দাগ হালকা করে\nকোলাজেন তৈরি বাড়ায় ও বলিরেখা দূর করে\nকোনো প্যারাবেন, সালফেট বা ক্ষতিকর কেমিক্যাল নেই',
        'regular_price': Decimal('1450.00'),
        'discount_price': Decimal('1150.00'),
        'primary_image': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 40,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.9'),
        'rating_count': 78,
        'sizes': ['30ml Glass Dropper']
    },
    {
        'name': 'আল্ট্রা ভেলভেট ম্যাট লিপস্টিক কালেকশন - ওয়াটারপ্রুফ',
        'cat_slug': 'lipsticks-makeup',
        'gender': 'women',
        'fabric': 'Moisturizing Velvet Matte with Shea Butter & Vit-E',
        'description': 'ঠোঁটকে শুষ্ক না করে নিখুঁত ভেলভেট ফিনিশ দেয়। ১২ ঘণ্টা দীর্ঘস্থায়ী ও ট্রান্সফার-প্রুফ। রাজকীয় রেড ও ন্যাচারাল ন্যুড শেড।',
        'features': 'স্মাজ ও ওয়াটারপ্রুফ ফর্মুলা\nশিয়া বাটার ও ভিটামিন ই সমৃদ্ধ\nকোনো ক্ষতিকর সীসা বা প্যারাবেন মুক্ত',
        'regular_price': Decimal('950.00'),
        'discount_price': Decimal('750.00'),
        'primary_image': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 35,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.9'),
        'rating_count': 51,
        'sizes': ['Ruby Red', 'Nude Rose', 'Berry Plum']
    },
    {
        'name': 'রয়্যাল অউদ অ্যান্ড অ্যাম্বার লাক্সারি পারফিউম (100ml)',
        'cat_slug': 'luxury-perfumes',
        'gender': 'unisex',
        'fabric': 'Extrait De Parfum (25% Fragrance Oil Concentration)',
        'description': 'রাজকীয় আভিজাত্যের অউদ, চন্দন ও মসৃণ ভ্যানিলার এক জাদুকরী মিশ্রণ। সারাদিন ধরে ছড়িয়ে দেবে দীর্ঘস্থায়ী সম্মোহনী সুবাস।',
        'features': '২৪ ঘণ্টার বেশি তীব্র স্থায়ী সুবাস\nটপ নোটস: বার্গামট ও জাফরান\nবেস নোটস: আগরউড (অউদ), অ্যাম্বার ও হোয়াইট মাস্ক',
        'regular_price': Decimal('2850.00'),
        'discount_price': Decimal('2350.00'),
        'primary_image': 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 22,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('5.0'),
        'rating_count': 62,
        'sizes': ['100ml EDP']
    },
]

ELECTRONICS_CATEGORIES = [
    {
        'name': 'ওয়্যারলেস ব্লুটুথ ইয়ারবাডস',
        'slug': 'wireless-earbuds',
        'gender': 'unisex',
        'image': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80',
        'description': 'অ্যাক্টিভ নয়েজ ক্যানসেলেশন (ANC), হাই-রেজ অডিও ও লো-লেটেন্সি গেমিং মোড সম্পন্ন ইয়ারবাডস।',
        'order': 1
    },
    {
        'name': 'ফাস্ট চার্জার ও পাওয়ারব্যাংক',
        'slug': 'powerbanks-chargers',
        'gender': 'unisex',
        'image': 'https://images.unsplash.com/photo-1609592424364-75eb94432a4e?w=800&auto=format&fit=crop&q=80',
        'description': '২০,০০০ এমএএইচ ৬৫ ওয়াট পিডি সুপারফাস্ট চার্জিং পাওয়ার ব্যাংক ও GaN এডাপ্টার।',
        'order': 2
    },
    {
        'name': 'স্মার্ট লাইফস্টাইল টেক গ্যাজেটস',
        'slug': 'smart-lifestyle-gadgets',
        'gender': 'unisex',
        'image': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&auto=format&fit=crop&q=80',
        'description': 'ওয়্যারলেস চার্জিং ডক, ম্যাগনেটিক কার মাউন্ট ও আধুনিক স্মার্ট ডেস্ক এক্সেসরিজ।',
        'order': 3
    },
]

ELECTRONICS_PRODUCTS = [
    {
        'name': 'প্রো হাই-ফাই অ্যাক্টিভ নয়েজ ক্যানসেলিং ওয়্যারলেস ইয়ারবাডস',
        'cat_slug': 'wireless-earbuds',
        'gender': 'unisex',
        'fabric': 'Titanium Diaphragm Drivers & Smart Touch Sensor',
        'description': '-৩৫dB পর্যন্ত বাহিরের কোলাহল ফিল্টার করে দেয় গভীর বাস ও ক্রিস্টাল ক্লিয়ার মিউজিক এক্সপেরিয়েন্স। কোয়াড মাইক সহ নিখুঁত কলিং।',
        'features': 'অ্যাক্টিভ নয়েজ ক্যানসেলেশন ও ট্রান্সপারেন্সি মোড\n৩৬ ঘণ্টা মোট প্লেব্যাক (টাইপ-সি ফাস্ট চার্জিং)\n৩৮ms আল্ট্রা লো-লেটেন্সি গেমিং মোড',
        'regular_price': Decimal('2850.00'),
        'discount_price': Decimal('2250.00'),
        'primary_image': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 35,
        'is_eid_special': True,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.9'),
        'rating_count': 84,
        'sizes': ['Pearl White', 'Matte Black']
    },
    {
        'name': '২০,০০০ এমএএইচ ৬৫ ওয়াট পিডি সুপারফাস্ট চার্জিং পাওয়ার ব্যাংক',
        'cat_slug': 'powerbanks-chargers',
        'gender': 'unisex',
        'fabric': 'Fireproof PC+ABS & Intelligent Safety Chip',
        'description': 'ল্যাপটপ, ম্যাকবুক এবং যেকোনো স্মার্টফোন ফুল স্পিডে চার্জ করার জন্য ৬৫ ওয়াট পাওয়ার ডেলিভারি সাপোর্ট। ডিজিটাল এলইডি ডিসপ্লে।',
        'features': 'ল্যাপটপ ও ফোন একই সাথে চার্জ করার সুবিধা\n৩টি আউটপুট পোর্ট (২x Type-C, ১x USB-A)\nওভার-হিট ও ওভার-ভোল্টেজ প্রটেকশন',
        'regular_price': Decimal('3200.00'),
        'discount_price': Decimal('2690.00'),
        'primary_image': 'https://images.unsplash.com/photo-1609592424364-75eb94432a4e?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 28,
        'is_eid_special': False,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.9'),
        'rating_count': 91,
        'sizes': ['20,000mAh 65W']
    },
    {
        'name': 'থ্রি-ইন-ওয়ান ম্যাগনেটিক ওয়্যারলেস ফাস্ট চার্জিং ডক স্টেশন',
        'cat_slug': 'smart-lifestyle-gadgets',
        'gender': 'unisex',
        'fabric': 'Aviation Aluminium Alloy & Soft Silicone Pad',
        'description': 'একসাথে ফোন, স্মার্টওয়াচ এবং ইয়ারবাডস কোনো তারের ঝামেলা ছাড়াই দ্রুত চার্জ করুন। টেবিলের সৌন্দর্য বৃদ্ধি করে ফোল্ডেবল ডিজাইন।',
        'features': '১৫ ওয়াট ম্যাগ-সেফ সুপার স্ট্রং ম্যাগনেট সাপোর্ট\nফোন ভার্টিক্যাল ও হরিজন্টাল রেখে চার্জের সুবিধা\nস্মার্ট টেম্পারেচার কন্ট্রোলিং সার্কিট',
        'regular_price': Decimal('2450.00'),
        'discount_price': Decimal('1950.00'),
        'primary_image': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&auto=format&fit=crop&q=80',
        'hover_image': '',
        'stock': 20,
        'is_eid_special': False,
        'is_bestseller': True,
        'is_new': True,
        'rating': Decimal('4.8'),
        'rating_count': 39,
        'sizes': ['Space Gray', 'Silver']
    },
]


def build_database(target_filename, categories_list, products_list, reviews_list):
    print(f"\n📦 Building standalone database: {target_filename}...")
    target_path = BASE_DIR / target_filename
    if os.path.exists(target_path):
        os.remove(target_path)

    # Temporarily switch database target
    connection.close()
    settings.DATABASES['default']['NAME'] = target_path
    
    # Run migrations on new target database
    call_command('migrate', verbosity=0)

    # Seed Admin & Coupons
    create_common_data()

    # Seed Categories
    cats = {}
    for c_data in categories_list:
        cat = Category.objects.create(
            name=c_data['name'],
            slug=c_data['slug'],
            niche=c_data.get('niche', target_filename.split('_')[1].split('.')[0] if '_' in target_filename else 'clothing'),
            gender=c_data.get('gender', 'unisex'),
            image=c_data['image'],
            description=c_data['description'],
            order=c_data['order'],
            is_featured=True
        )
        cats[c_data['slug']] = cat

    # Seed Products
    prods_to_create = []
    for p_raw in products_list:
        p_copy = p_raw.copy()
        cat_slug = p_copy.pop('cat_slug')
        p_copy['category'] = cats[cat_slug]
        prods_to_create.append(p_copy)
    
    seed_products(cats, prods_to_create)

    # Seed Reviews
    first_prod = Product.objects.first()
    if first_prod and reviews_list:
        for rev in reviews_list:
            Review.objects.create(
                product=first_prod,
                name=rev['name'],
                city=rev['city'],
                rating=rev['rating'],
                comment=rev['comment']
            )

    # Seed Sample Orders for Dashboard
    all_prods = list(Product.objects.all())
    if len(all_prods) >= 2:
        seed_sample_orders(all_prods[0], all_prods[1])
    elif len(all_prods) == 1:
        seed_sample_orders(all_prods[0], all_prods[0])

    print(f"   ✓ {target_filename} created with {Category.objects.count()} categories and {Product.objects.count()} products.")
    connection.close()


def main():
    print("🚀 Generating separate standalone databases for each niche...")

    # 1. Clothing DB
    clothing_reviews = [
        {'name': 'সাকিব আল হাসান', 'city': 'গুলশান, ঢাকা', 'rating': 5, 'comment': 'পাঞ্জাবির কাপড় এবং এমব্রয়ডারি অসম্ভব সুন্দর! সাইজ একদম পারফেক্ট হয়েছে। অর্ডার করার পরের দিনই বনানীতে ডেলিভারি পেয়েছি।'},
        {'name': 'ফারহানা ইয়াসমিন', 'city': 'পাঁচলাইশ, চট্টগ্রাম', 'rating': 5, 'comment': 'জামদানি শাড়িটির জমিন ও পাড় এত নিখুঁত যে পরিবারের সবাই প্রশংসা করেছে। খাঁটি ঢাকাই বুনন। ধন্যবাদ AHMZ!'},
        {'name': 'তানভীর চৌধুরী', 'city': 'উপশহর, সিলেট', 'rating': 5, 'comment': 'গিজা কটন পাঞ্জাবিটা গরমে পরে খুবই আরাম লেগেছে। ক্যাশ অন ডেলিভারিতে চেক করে নিতে পেরেছি। বেস্ট সার্ভিস।'},
    ]
    build_database('db_clothing.sqlite3', CLOTHING_CATEGORIES, CLOTHING_PRODUCTS, clothing_reviews)

    # 2. Shoes DB
    shoes_reviews = [
        {'name': 'মাহমুদুল হক', 'city': 'ধানমন্ডি, ঢাকা', 'rating': 5, 'comment': 'লেদার লোফারের ফিনিশিং অসাধারণ! পুরো দিন পায়ে দিয়েও একটুও ব্যথা লাগেনি। খাঁটি চামড়ার অনুভূতি।'},
        {'name': 'রাকিব আহমেদ', 'city': 'উত্তরা, ঢাকা', 'rating': 5, 'comment': 'অক্সফোর্ড শু জোড়া সাইজ ৪২ একদম পারফেক্ট হয়েছে। বিয়েতে সবাই প্রশংসা করেছে।'},
        {'name': 'ইমরান খান', 'city': 'খুলনা সদর', 'rating': 5, 'comment': 'স্নিকার্স খুব লাইটওয়েট এবং কুশনিং খুবই নরম। ক্যাশ অন ডেলিভারিতে দ্রুত পেয়েছি।'},
    ]
    build_database('db_shoes.sqlite3', SHOES_CATEGORIES, SHOES_PRODUCTS, shoes_reviews)

    # 3. Watches DB
    watches_reviews = [
        {'name': 'তানজিমুল হক', 'city': 'বনানী, ঢাকা', 'rating': 5, 'comment': 'গ্রিন ডায়ালের ক্রোনোগ্রাফ ঘড়িটা হাতে পেয়ে অবাক হয়েছি! একদম প্রিমিয়াম লাক্সারি লুক।'},
        {'name': 'আসিফ জামান', 'city': 'জিইসি মোড়, চট্টগ্রাম', 'rating': 5, 'comment': 'অটোমেটিক স্কেলিটন ঘড়িটার মেকানিজম জাস্ট ওয়াও! ব্যাটারি ছাড়াই চলছে। হেভি কোয়ালিটি।'},
        {'name': 'শাহরিয়ার কবির', 'city': 'রাজশাহী', 'rating': 5, 'comment': 'স্মার্টওয়াচের AMOLED ডিসপ্লে রোদেও একদম ক্লিয়ার দেখা যায় এবং ব্যাটারি ব্যাকআপ ৫ দিন পাচ্ছি।'},
    ]
    build_database('db_watches.sqlite3', WATCHES_CATEGORIES, WATCHES_PRODUCTS, watches_reviews)

    # 4. Cosmetics DB
    cosmetics_reviews = [
        {'name': 'সাদিয়া তাসনিম', 'city': 'বনশ্রী, ঢাকা', 'rating': 5, 'comment': 'ভিটামিন সি সিরাম ব্যবহারের ২ সপ্তাহেই ত্বকের ব্রাইটনেস বেড়েছে। ১০০% অথেন্টিক প্রোডাক্ট।'},
        {'name': 'নুসরাত জাহান', 'city': 'মতিঝিল, ঢাকা', 'rating': 5, 'comment': 'ভেলভেট ম্যাট লিপস্টিকটা সারাদিন একদম স্মাজ হয় না এবং ঠোঁট নরম রাখে। দারুণ প্যাকেজিং।'},
        {'name': 'জান্নাতুল ফেরদৌস', 'city': 'সিলেট', 'rating': 5, 'comment': 'রয়্যাল অউদ পারফিউমের ঘ্রাণ ২৪ ঘণ্টারও বেশি টিকে থাকে। অসাধারণ সুবাস!'},
    ]
    build_database('db_cosmetics.sqlite3', COSMETICS_CATEGORIES, COSMETICS_PRODUCTS, cosmetics_reviews)

    # 5. Electronics DB
    electronics_reviews = [
        {'name': 'কাজী রেজোয়ান', 'city': 'মিরপুর ১০, ঢাকা', 'rating': 5, 'comment': 'ইয়ারবাডসের অ্যাক্টিভ নয়েজ ক্যানসেলেশন ও বাসের কোয়ালিটি মাইন্ড ব্লোয়িং। কলিংয়ে কোনো নয়েজ নেই।'},
        {'name': 'সৌরভ দত্ত', 'city': 'আগ্রাবাদ, চট্টগ্রাম', 'rating': 5, 'comment': '৬৫ ওয়াট পাওয়ার ব্যাংক দিয়ে আমার ম্যাকবুক ও স্যামসাং দুটোই সুপারফাস্ট চার্জ হচ্ছে। বেস্ট গ্যাজেট!'},
        {'name': 'আহনাফ হাসান', 'city': 'উত্তরা, ঢাকা', 'rating': 5, 'comment': 'থ্রি-ইন-ওয়ান ওয়্যারলেস চার্জিং ডক টেবিলে সব তারের ঝামেলা মিটিয়ে দিয়েছে। ফিনিশিং প্রিমিয়াম।'},
    ]
    build_database('db_electronics.sqlite3', ELECTRONICS_CATEGORIES, ELECTRONICS_PRODUCTS, electronics_reviews)

    # 6. Mega Store DB (All combined)
    all_cats = CLOTHING_CATEGORIES + SHOES_CATEGORIES + WATCHES_CATEGORIES + COSMETICS_CATEGORIES + ELECTRONICS_CATEGORIES
    all_prods = CLOTHING_PRODUCTS + SHOES_PRODUCTS + WATCHES_PRODUCTS + COSMETICS_PRODUCTS + ELECTRONICS_PRODUCTS
    all_reviews = clothing_reviews + shoes_reviews + watches_reviews + cosmetics_reviews + electronics_reviews
    build_database('db_mega_all.sqlite3', all_cats, all_prods, all_reviews)

    # Make clothing DB the active default db.sqlite3
    shutil.copyfile(BASE_DIR / 'db_clothing.sqlite3', BASE_DIR / 'db.sqlite3')
    print("\n🎉 All 6 standalone databases successfully generated!")
    print("👉 Default 'db.sqlite3' has been set to 'db_clothing.sqlite3'.")


if __name__ == '__main__':
    main()
