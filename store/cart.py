from decimal import Decimal
from store.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def _get_key(self, product_id, size='Regular', color='Default'):
        size_clean = str(size or 'Regular').strip()
        color_clean = str(color or 'Default').strip()
        return f"{product_id}_{size_clean}_{color_clean}"

    def add(self, product, size='Regular', color='Default', quantity=1, override_quantity=False):
        key = self._get_key(product.id, size, color)
        price = str(product.get_price())

        if key not in self.cart:
            self.cart[key] = {
                'product_id': product.id,
                'name': product.name,
                'sku': product.sku,
                'price': price,
                'size': str(size or 'Regular'),
                'color': str(color or 'Default'),
                'image': product.primary_image,
                'quantity': 0,
            }

        if override_quantity:
            self.cart[key]['quantity'] = int(quantity)
        else:
            self.cart[key]['quantity'] += int(quantity)

        if self.cart[key]['quantity'] <= 0:
            del self.cart[key]

        self.save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self.save()

    def update_quantity(self, key, quantity):
        if key in self.cart:
            qty = int(quantity)
            if qty > 0:
                self.cart[key]['quantity'] = qty
            else:
                del self.cart[key]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids).in_bulk()

        for key, item in self.cart.items():
            item_copy = item.copy()
            item_copy['key'] = key
            product = products.get(item['product_id'])
            item_copy['product'] = product
            item_copy['unit_price'] = Decimal(item['price'])
            item_copy['total_price'] = Decimal(item['price']) * item['quantity']
            yield item_copy

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_subtotal(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_items_list(self):
        return list(self.__iter__())
