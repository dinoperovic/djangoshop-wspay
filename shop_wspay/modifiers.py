# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from shop.modifiers.base import PaymentModifier
from shop_wspay.payment import WSPayPayment
from shop_wspay.conf import app_settings

try:
    from shop.serializers.cart import ExtraCartRow
except ImportError:
    # Fallback to django-shop version 0.9.x.
    from shop.rest.serializers import ExtraCartRow


class WSPayPaymentModifier(PaymentModifier):
    identifier = WSPayPayment.namespace
    payment_provider = WSPayPayment()
    commision_percentage = app_settings.COMMISION_PERCENTAGE

    def get_choice(self):
        return (self.identifier, app_settings.MODIFIER_CHOICE_TEXT)

    def is_disabled(self, cart):
        return cart.total == 0

    def add_extra_cart_row(self, cart, request):
        if not self.is_active(cart) or not self.commision_percentage:
            return
        amount = cart.total * Decimal(self.commision_percentage / 100.0)
        instance = {'label': _("+ %d%% handling fee") % self.commision_percentage, 'amount': amount}
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount
