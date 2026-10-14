from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from store.models import Category, Product, ProductVariant, Order, Coupon

class StoreEcommerceTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name="টেস্ট পাঞ্জাবি",
            gender="men",
            slug="test-panjabi"
        )
        self.product = Product.objects.create(
            name="প্রিমিয়াম টেস্ট পাঞ্জাবি",
            slug="premium-test-panjabi",
            sku="AHMZ-TEST-001",
            category=self.category,
            regular_price=Decimal("2500.00"),
            discount_price=Decimal("2000.00"),
            stock=15,
            primary_image="https://example.com/image.jpg",
            description="টেস্ট বিবরণী"
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size="40",
            color="Default",
            stock=10
        )
        self.coupon = Coupon.objects.create(
            code="EIDTEST",
            discount_percent=10,
            min_spend=Decimal("1000.00"),
            max_discount=Decimal("500.00"),
            is_active=True
        )

    def test_bengali_product_slug_generation(self):
        # Product created with pure Bengali title without manual slug
        bengali_product = Product.objects.create(
            name="খাঁটি ঢাকাই জামদানি",
            sku="AHMZ-JAM-99",
            category=self.category,
            regular_price=Decimal("4500.00"),
            stock=5,
            primary_image="https://example.com/jamdani.jpg",
            description="বিবরণ"
        )
        self.assertTrue(bool(bengali_product.slug))
        self.assertNotEqual(bengali_product.slug, "")
        url = reverse('store:product_detail', kwargs={'slug': bengali_product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_home_page(self):
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AHMZ")

    def test_product_list_page(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "প্রিমিয়াম টেস্ট পাঞ্জাবি")

    def test_product_detail_page(self):
        response = self.client.get(reverse('store:product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AHMZ-TEST-001")
        self.assertContains(response, "৳2000.00")

    def test_cart_operations_and_coupon(self):
        # 1. Add to cart
        add_url = reverse('store:add_to_cart', kwargs={'product_id': self.product.id})
        response = self.client.post(add_url, {'size': '40', 'quantity': 2})
        self.assertEqual(response.status_code, 302)

        # 2. View cart
        cart_url = reverse('store:cart_detail')
        response = self.client.get(cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "প্রিমিয়াম টেস্ট পাঞ্জাবি")
        self.assertContains(response, "40")

        # 3. Apply coupon
        coupon_url = reverse('store:apply_coupon')
        response = self.client.post(coupon_url, {'code': 'EIDTEST'})
        self.assertEqual(response.status_code, 302)

        # Re-check cart
        response = self.client.get(cart_url)
        self.assertContains(response, "EIDTEST")

    def test_checkout_and_order_tracking(self):
        # Add item first
        self.client.post(reverse('store:add_to_cart', kwargs={'product_id': self.product.id}), {'size': '40', 'quantity': 1})
        
        # Post checkout form
        checkout_url = reverse('store:checkout')
        data = {
            'full_name': 'তানজিম আহমেদ',
            'phone': '01700112233',
            'email': 'tanjim@example.com',
            'division': 'Dhaka',
            'district': 'Dhaka',
            'delivery_address': 'ধানমন্ডি ৩২, ঢাকা',
            'delivery_area': 'inside_dhaka',
            'payment_method': 'cod',
        }
        response = self.client.post(checkout_url, data)
        self.assertEqual(response.status_code, 302)

        # Verify order exists
        order = Order.objects.filter(phone='01700112233').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.delivery_area, 'inside_dhaka')
        self.assertEqual(order.shipping_cost, Decimal('60.00'))
        self.assertEqual(order.items.count(), 1)

        # Track order
        track_url = reverse('store:track_order')
        response = self.client.get(f"{track_url}?order_number={order.order_number}&phone={order.phone}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)

    def test_dashboard_views(self):
        # Test dashboard overview
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ওভারভিউ")

        # Test dashboard orders
        response = self.client.get(reverse('dashboard:orders'))
        self.assertEqual(response.status_code, 200)

        # Test dashboard products
        response = self.client.get(reverse('dashboard:product_management'))
        self.assertEqual(response.status_code, 200)

    def test_language_switch(self):
        # Default is Bangla
        res = self.client.get(reverse('store:home'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['CURRENT_LANG'], 'bn')

        # Switch to English
        res = self.client.get(reverse('store:switch_language', kwargs={'lang': 'en'}))
        self.assertEqual(res.status_code, 302)

        # Check Home is now in English
        res = self.client.get(reverse('store:home'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['CURRENT_LANG'], 'en')
        self.assertContains(res, "Shop All")
        self.assertContains(res, "Artisan Elegance")

        # Switch back to Bangla
        res = self.client.get(reverse('store:switch_language', kwargs={'lang': 'bn'}))
        self.assertEqual(res.status_code, 302)
        res = self.client.get(reverse('store:home'))
        self.assertEqual(res.context['CURRENT_LANG'], 'bn')
        self.assertContains(res, "সকল পোশাক")
