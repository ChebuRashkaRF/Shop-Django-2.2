from decimal import Decimal
from django.conf import settings

from shop.models import Product
from coupons.models import Coupon


class Cart(object):
    """Корзина покупателя"""

    def __init__(self, request):
        """Инициализация объекта корзины."""

        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Сохраняем в сессии пустую корзину.
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # Сохраняем купон.
        self.coupon_id = self.session.get('coupon_id')
        # print(*self.session.keys())

    def add(self, product, quantity=1, update_quantity=False):
        """Добавление товара в корзину или обновление его количества."""

        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
         # Помечаем сессию как измененную
         self.session.modified = True

    def remove(self, product):
        """Удаление товара из корзины."""

        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Проходим по товарам корзины и получаем соответствующие объекты Product.

        """

        product_ids = self.cart.keys()
        # Получаем объекты модели Product и передаем их в корзину.
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Возвращает общее количество товаров в корзине."""

        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Возвращает общую стоимость корзины"""

        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Очистка корзины.
        del self.session[settings.CART_SESSION_ID]
        # del self.session['coupon_id']
        self.save()

    @property
    def coupon(self):
        """Свойство будет возвращать соответствующий объект купона"""

        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    def get_discount(self):
        """возвращает размер скидки"""

        if self.coupon:
            return (self.coupon.discount / Decimal('100')) \
                * self.get_total_price()
        return Decimal('0')

    def get_total_price_after_discount(self):
        """
        Возвращает общую стоимость товаров в корзине с учетом скидки по купону

        """

        return self.get_total_price() - self.get_discount()