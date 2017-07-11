# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

# WSPay shop ID.
SHOP_ID = settings.SHOP_WSPAY_ID

# WSPay secret key.
SECRET_KEY = settings.SHOP_WSPAY_SECRET_KEY

# Set to 'https://formtest.wspay.biz/Authorization.aspx' for testing.
FORM_URL = getattr(settings, 'SHOP_WSPAY_FORM_URL', 'https://form.wspay.biz/Authorization.aspx')

# Set if a separate payment view should be rendered before sending to GestPay.
PAYMENT_VIEW = getattr(settings, 'SHOP_WSPAY_PAYMENT_VIEW', False)

# Url of a cart, used to redirect in some cases.
CART_URL = getattr(settings, 'SHOP_WSPAY_CART_URL', getattr(settings, 'SHOP_CART_URL', 'shop:cart-list'))

# Thank you url, if None latest order is used.
THANK_YOU_URL = getattr(settings, 'SHOP_WSPAY_THANK_YOU_URL', getattr(settings, 'SHOP_THANK_YOU_URL', None))

# Set to add commision percentage for purchase via GestPay.
COMMISION_PERCENTAGE = getattr(settings, 'SHOP_WSPAY_COMMISION_PERCENTAGE', None)

# Text displayed as a choice for selecting GestPay payment.
MODIFIER_CHOICE_TEXT = getattr(settings, 'SHOP_WSPAY_MODIFIER_CHOICE_TEXT', 'WSPay')

# Message added to django messages framework if there's a transaction error.
ERROR_MESSAGE = getattr(settings, 'SHOP_WSPAY_ERROR_MESSAGE', None)

# Message added to django messages framework if transaction is canceled.
CANCEL_MESSAGE = getattr(settings, 'SHOP_WSPAY_CANCEL_MESSAGE', None)

# Message added to django messages framework transaction is successful.
SUCCESS_MESSAGE = getattr(settings, 'SHOP_WSPAY_SUCCESS_MESSAGE', None)
