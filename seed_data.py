import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Category, Product, ProductVariant, Coupon, Order, OrderItem, Review
from accounts.models import UserProfile

def seed():
    print("🌱 Starting database seeding for AHMZ Lifestyle...")

    # 1. Superuser
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
        print("✅ Superuser created: admin / admin123")

    # 2. Categories
    categories_data = [
        {
            'name': 'পাঞ্জাবি ও কাবলি (Panjabi & Kabli)',
            'gender': 'men',
            'image': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&auto=format&fit=crop&q=80',
            'description': 'খাঁটি মিশরীয় গিজা কটন, সুতি জ্যাকার্ড ও ঐতিহ্যবাহী এমব্রয়ডারি করা পাঞ্জাবি কালেকশন।',
            'order': 1
        },
        {
            'name': 'জামদানি ও এক্সক্লুসিভ শাড়ি (Saree)',
            'gender': 'women',
            'image': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80',
            'description': 'ঐতিহ্যবাহী ঢাকাই জামদানি, মসলিন সিল্ক ও কাঞ্চিপুরম ডিজাইনার শাড়ি।',
            'order': 2
        },
        {
            'name': 'সালোয়ার কামিজ ও কুর্তি (Salwar & Kurti)',
            'gender': 'women',
            'image': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80',
            'description': 'আধুনিক তরুণীদের জন্য আরামদায়ক লিনেন কুর্তি ও থ্রি-পিস সেট।',
            'order': 3
        },
        {
            'name': 'ক্যাজুয়াল পোলো ও প্রিমিয়াম টি-শার্ট',
            'gender': 'unisex',
            'image': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80',
            'description': '২২০ জিএসএম ভারী সুতি পোলো শার্ট ও প্রিমিয়াম ড্রপ-শোল্ডার টি-শার্ট।',
            'order': 4
        },
    ]

    cats = {}
    for c_data in categories_data:
        cat, _ = Category.objects.get_or_create(
            name=c_data['name'],
            defaults={
                'gender': c_data['gender'],
                'image': c_data['image'],
                'description': c_data['description'],
                'order': c_data['order']
            }
        )
        cats[c_data['name']] = cat
    print("✅ Categories created.")

    # 3. Products
    products_data = [
        # Men's Panjabi
        {
            'name': 'রয়্যাল এমব্রয়ডারি জ্যাকার্ড পাঞ্জাবি - ডিপ নেভি ব্লু',
            'category': cats['পাঞ্জাবি ও কাবলি (Panjabi & Kabli)'],
            'gender': 'men',
            'fabric': '100% Fine Combed Jacquard Cotton',
            'description': 'আভিজাত্য ও ঐতিহ্যের অপরূপ সমন্বয়। নেকলাইনে নিখুঁত কারুকাজ ও প্রিমিয়াম মেটালিক বোতাম সহ আকর্ষণীয় ডিপ নেভি ব্লু পাঞ্জাবি। যেকোনো উৎসব বা জুম্মার দিনে আরামের নিশ্চয়তা।',
            'features': 'মান্দারিন কলার ও থ্রেড এমব্রয়ডারি নকশা\nউচ্চমানের অ্যান্টি-রিঙ্কেল সুতি ফেব্রিক\nদুই পাশে পকেট ও ডাবল স্টিচিং\nড্রাই ওয়াশ বা হালকা পানিতে ধোয়া উপযোগী',
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
            'category': cats['পাঞ্জাবি ও কাবলি (Panjabi & Kabli)'],
            'gender': 'men',
            'fabric': '100% Pure Egyptian Giza Cotton',
            'description': 'সাদা রঙের চিরন্তন স্নিগ্ধতা। গ্রীষ্মের তীব্র রোদ কিংবা ঈদের সকালের নামাজ—১০০% গিজা কটনের এই পাঞ্জাবি আপনার ব্যক্তিত্বকে দেবে রাজকীয় রূপ।',
            'features': 'সফট কটন ফিনিশিং যা সারাদিন শীতল অনুভূতি দেয়\nহাতে বসানো স্ফটিক বোতাম\nসেমি-ফিটেড আরামদায়ক কাটিং\nমেশিন ও হ্যান্ড ওয়াশ সমর্থিত',
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
            'name': 'এমারেল্ড গ্রিন কাবলি সেট উইথ পায়জামা',
            'category': cats['পাঞ্জাবি ও কাবলি (Panjabi & Kabli)'],
            'gender': 'men',
            'fabric': 'Premium Viscose Blend Fabric',
            'description': 'ট্রেন্ডি ও স্মার্ট কাবলি সেট। ডিপ পান্না সবুজ রঙের সাথে ম্যাচিং পায়জামা অন্তর্ভুক্ত। চেস্ট পকেট ও প্রিমিয়াম স্ন্যাপ বাটনে তৈরি।',
            'features': 'ম্যাচিং ট্রাউজার বা পায়জামা সাথে দেওয়া আছে\nবুক পকেট ও আধুনিক শার্ট-কাফ স্লিভ\nরঙ পাকা ও টেকসই ফেব্রিক\nযেকোনো বিয়ে ও পারিবারিক অনুষ্ঠানে মানানসই',
            'regular_price': Decimal('3600.00'),
            'discount_price': Decimal('3150.00'),
            'primary_image': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&auto=format&fit=crop&q=80',
            'hover_image': '',
            'stock': 12,
            'is_eid_special': True,
            'is_bestseller': False,
            'is_new': True,
            'rating': Decimal('4.9'),
            'rating_count': 16,
            'sizes': ['40', '42', '44']
        },

        # Women's Saree
        {
            'name': 'ঐতিহ্যবাহী ঢাকাই জামদানি শাড়ি - রয়েল গোল্ডেন জারি',
            'category': cats['জামদানি ও এক্সক্লুসিভ শাড়ি (Saree)'],
            'gender': 'women',
            'fabric': '100% Handwoven Muslin & Cotton Jamdani',
            'description': 'রূপগঞ্জের তাঁতিদের হাতে বোনা খাঁটি ঢাকাই জামদানি। সূক্ষ্ম গোল্ডেন জরি ও সুতার বুননে তৈরি এই শাড়ি প্রতিটি নারীর আভিজাত্যের প্রতীক। ম্যাচিং ব্লাউজ পিস সহ।',
            'features': 'সম্পূর্ণ হস্তনির্মিত তাঁতের জামদানি বুনন\nউজ্জ্বল ও দীর্ঘস্থায়ী নকশা\nদৈর্ঘ্য: ১২ হাত (ব্লাউজ পিস সহ)\nশুধু ড্রাই ক্লিন গ্রহণযোগ্য',
            'regular_price': Decimal('5500.00'),
            'discount_price': Decimal('4750.00'),
            'primary_image': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80',
            'hover_image': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80',
            'stock': 8,
            'is_eid_special': True,
            'is_bestseller': True,
            'is_new': True,
            'rating': Decimal('5.0'),
            'rating_count': 42,
            'sizes': ['Free Size']
        },
        {
            'name': 'রাজস্থানি হাফ সিল্ক উৎসব শাড়ি - মেরুন রেড',
            'category': cats['জামদানি ও এক্সক্লুসিভ শাড়ি (Saree)'],
            'gender': 'women',
            'fabric': 'Semi-Pure Silk Blend with Zari Border',
            'description': 'গভীর মেরুন রঙের জমিনে সোনালি সুতার কাজ। হালকা ও পরতে অত্যন্ত আরামদায়ক। বিয়ে, রিসেপশন বা উৎসবের সান্ধ্যকালীন আয়োজনে চোখ ধাঁধানো লুক।',
            'features': 'সিল্কি টেক্সচার ও চমৎকার ড্র্যাপ\nআঁচলে বৈচিত্র্যময় ট্র্যাডিশনাল ট্যাসেল\nব্লাউজ পিস সাথে সংযুক্ত\nসহজে কুঁচি ধরে রাখা সম্ভব',
            'regular_price': Decimal('3200.00'),
            'discount_price': Decimal('2650.00'),
            'primary_image': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80',
            'hover_image': '',
            'stock': 14,
            'is_eid_special': False,
            'is_bestseller': True,
            'is_new': False,
            'rating': Decimal('4.7'),
            'rating_count': 22,
            'sizes': ['Free Size']
        },

        # Women's Salwar & Kurti
        {
            'name': 'ডিজাইনার লিনেন ফেস্টিভ কুর্তি - স্কাই ব্লু',
            'category': cats['সালোয়ার কামিজ ও কুর্তি (Salwar & Kurti)'],
            'gender': 'women',
            'fabric': 'Organic Breathable Linen',
            'description': 'গরমে সর্বোচ্চ স্বস্তি ও আধুনিক স্টাইল একসাথে। স্কাই ব্লু লিনেন ফ্যাব্রিকে সূক্ষ্ম প্যাচওয়ার্ক ও ফ্রন্ট বাটন ডিটেইলিং। জিন্স বা লেগিংসের সাথে মানানসই।',
            'features': 'ব্রিদেবল লিনেন যা ঘাম শোষণ করে\nA-লাইন কাটিং ও সাইড স্লিট\nথ্রি-কোয়ার্টার হাতা\nদৈনন্দিন অফিস ও ভার্সিটির জন্য দারুণ পছন্দ',
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

        # Casual Polo & Tee
        {
            'name': 'সিগনেচার পিক পোলো শার্ট - ফরেস্ট গ্রিন',
            'category': cats['ক্যাজুয়াল পোলো ও প্রিমিয়াম টি-শার্ট'],
            'gender': 'unisex',
            'fabric': '220 GSM 100% Combed Pique Cotton',
            'description': 'আন্তর্জাতিক মানের ২২০ জিএসএম পিক কটন পোলো। কোনো লিন্ট উঠবে না ও বারবার ধোয়ার পরেও কলার ঢিলে হবে না। স্মার্ট ক্যাজুয়াল ওয়্যার।',
            'features': 'ডাবল রাইস পিক নিটিং\nস্ট্রং কলার ও ২-বাটন প্লাকেট\nএনজাইম ওয়াশড আল্ট্রা-সফট ফিনিশ\nকালার ফাস্টনেস শতভাগ গ্যারান্টি',
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
        {
            'name': 'ঢাকা ড্রপ-শোল্ডার ওভারসাইজড হেভি টি-শার্ট - ব্ল্যাক',
            'category': cats['ক্যাজুয়াল পোলো ও প্রিমিয়াম টি-শার্ট'],
            'gender': 'unisex',
            'fabric': '240 GSM Combed Compact Cotton',
            'description': 'স্ট্রিটওয়্যার ট্রেন্ডের শীর্ষ পছন্দ। ড্রপ শোল্ডার ও আরামদায়ক ওভারসাইজড কাটে তৈরি ২৪০ জিএসএম কটন টি-শার্ট। খাঁটি আধুনিক বাংলাদেশি স্ট্রিট স্টাইল।',
            'features': 'ভারী টেকসই ২৪০ জিএসএম সুতি ফেব্রিক\nড্রপ শোল্ডার বক্সি ফিট\nলাইক্রা রিবড নেকলাইন\nপ্রিন্ট ও ফ্যাব্রিক লাইফটাইম লাস্টিং',
            'regular_price': Decimal('890.00'),
            'discount_price': Decimal('690.00'),
            'primary_image': 'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800&auto=format&fit=crop&q=80',
            'hover_image': '',
            'stock': 40,
            'is_eid_special': False,
            'is_bestseller': True,
            'is_new': True,
            'rating': Decimal('4.8'),
            'rating_count': 64,
            'sizes': ['M', 'L', 'XL']
        }
    ]

    for p_info in products_data:
        sizes = p_info.pop('sizes', ['40', '42'])
        sku = f"AHMZ-{p_info['name'][:3].upper()}-{Product.objects.count() + 1:04d}"
        prod, created = Product.objects.get_or_create(
            name=p_info['name'],
            defaults={
                'sku': sku,
                **p_info
            }
        )
        if created:
            for s in sizes:
                ProductVariant.objects.create(
                    product=prod,
                    size=s,
                    color='Default',
                    stock=prod.stock // len(sizes) if len(sizes) > 0 else prod.stock
                )
    print("✅ Products & variants created.")

    # 4. Coupons
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
    print("✅ Coupons created: EID2026 (10%), AHMZ15 (15%).")

    # 5. Reviews
    sample_product = Product.objects.first()
    if sample_product and not Review.objects.exists():
        reviews = [
            {'name': 'সাকিব আল হাসান', 'city': 'গুলশান, ঢাকা', 'rating': 5, 'comment': 'পাঞ্জাবির কাপড় এবং এমব্রয়ডারি অসম্ভব সুন্দর! সাইজ একদম পারফেক্ট হয়েছে। অর্ডার করার পরের দিনই বনানীতে ডেলিভারি পেয়েছি।'},
            {'name': 'ফারহানা ইয়াসমিন', 'city': 'পাঁচলাইশ, চট্টগ্রাম', 'rating': 5, 'comment': 'জামদানি শাড়িটির জমিন ও পাড় এত নিখুঁত যে পরিবারের সবাই প্রশংসা করেছে। খাঁটি ঢাকাই বুনন। ধন্যবাদ AHMZ!'},
            {'name': 'তানভীর চৌধুরী', 'city': 'উপশহর, সিলেট', 'rating': 5, 'comment': 'গিজা কটন পাঞ্জাবিটা গরমে পরে খুবই আরাম লেগেছে। ক্যাশ অন ডেলিভারিতে চেক করে নিতে পেরেছি। বেস্ট সার্ভিস।'},
            {'name': 'মাহমুদুল হক', 'city': 'ধানমন্ডি, ঢাকা', 'rating': 5, 'comment': 'পোলো শার্টের ফেব্রিক কোয়ালিটি এবং কলার ফিনিশিং ব্র্যান্ডেড শপের চেয়েও ভালো। আবার অর্ডার করবো ইনশাআল্লাহ।'},
        ]
        for rev in reviews:
            Review.objects.create(
                product=sample_product,
                name=rev['name'],
                city=rev['city'],
                rating=rev['rating'],
                comment=rev['comment'],
            )
        print("✅ Sample customer reviews created.")

    # 6. Sample Realistic Orders (For Dashboard Demo)
    if not Order.objects.exists():
        first_product = Product.objects.first()
        second_product = Product.objects.all()[1] if Product.objects.count() > 1 else first_product

        # Order 1: Delivered (COD, Dhaka)
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
            subtotal=Decimal('2450.00'),
            discount_amount=Decimal('245.00'),
            total_amount=Decimal('2265.00'),
            coupon_code='EID2026',
            payment_method='cod',
            payment_status='paid',
            status='delivered',
            courier_tracking_id='PATHAO-DK-9082',
            admin_notes='ডেলিভারি সম্পন্ন হয়েছে এবং টাকা রিসিভড।'
        )
        OrderItem.objects.create(
            order=o1, product=first_product, product_name=first_product.name,
            product_sku=first_product.sku, size='42', price=Decimal('2450.00'), quantity=1, subtotal=Decimal('2450.00')
        )

        # Order 2: Shipped via Steadfast (bKash, Chittagong)
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
            subtotal=Decimal('3150.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('3270.00'),
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
            product_sku=second_product.sku, size='40', price=Decimal('3150.00'), quantity=1, subtotal=Decimal('3150.00')
        )

        # Order 3: Pending (Needs Call Confirm)
        o3 = Order.objects.create(
            order_number='AHMZ-79105',
            full_name='তাহমিনা রহমান',
            phone='01912334455',
            email='tahmina@gmail.com',
            division='Dhaka',
            district='Dhaka',
            delivery_address='বাড়ি নং ৭, রোড নং ১২, ধানমন্ডি, ঢাকা',
            delivery_area='inside_dhaka',
            shipping_cost=Decimal('60.00'),
            subtotal=Decimal('4750.00'),
            discount_amount=Decimal('475.00'),
            total_amount=Decimal('4335.00'),
            coupon_code='EID2026',
            payment_method='cod',
            payment_status='unpaid',
            status='pending',
            customer_notes='বিকেলে ফোন দিয়ে ডেলিভারি করবেন প্লিজ।'
        )
        OrderItem.objects.create(
            order=o3, product=first_product, product_name=first_product.name,
            product_sku=first_product.sku, size='40', price=Decimal('4750.00'), quantity=1, subtotal=Decimal('4750.00')
        )
        print("✅ Sample realistic orders created with bKash and COD.")

    print("🎉 Seeding complete successfully!")

if __name__ == '__main__':
    seed()
