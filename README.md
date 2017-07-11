# djangoshop-wspay

[![PyPI version](https://img.shields.io/pypi/v/djangoshop-wspay.svg)](https://pypi.python.org/pypi/djangoshop-wspay)

**[WSPay](https://www.wspay.info/) Payment Integration for [djangoSHOP](http://www.django-shop.org).**

---

## Requirements

* [django-shop]

## Installation

Install using *pip*:

```bash
pip install djangoshop-wspay
```

Add the following to your settings:

```python
INSTALLED_APPS += ['shop_wspay']
SHOP_CART_MODIFIERS += ['shop_wspay.modifiers.WSPayPaymentModifier']
SHOP_ORDER_WORKFLOWS += ['shop_wspay.payment.WSPayWorkflowMixin']
SHOP_DEFAULT_CURRENCY = 'HRK'  # WSPay requires you to send amount in Croatian kuna.
SHOP_WSPAY_SHOP_ID = '<shopID>'  # WSPay shop ID.
SHOP_WSPAY_SECRET_KEY = '<secretKey>'  # WSPay secret key.
```

Additional settings with defaults:

```python
SHOP_WSPAY_FORM_URL = 'https://form.wspay.biz/Authorization.aspx'  # Set to 'https://formtest.wspay.biz/Authorization.aspx' for testing.
SHOP_WSPAY_PAYMENT_VIEW = False  # Set if a separate payment view should be rendered before sending to wspay.
SHOP_WSPAY_CART_URL = SHOP_CART_URL = 'shop:cart-list'  # Url of a cart, used to redirect in some cases.
SHOP_WSPAY_THANK_YOU_URL = SHOP_THANK_YOU_URL = None  # Thank you url, if None latest order is used.
SHOP_WSPAY_COMMISION_PERCENTAGE = None  # Set to add commision percentage for purchase via WSPay.
SHOP_WSPAY_MODIFIER_CHOICE_TEXT = 'WSPay'  # Text displayed as a choice for selecting wspay payment.
SHOP_WSPAY_ERROR_MESSAGE = None  # Message added to django messages framework if there's a transaction error.
SHOP_WSPAY_CANCEL_MESSAGE = None  # Message added to django messages framework if transaction is canceled.
SHOP_WSPAY_SUCCESS_MESSAGE = None  # Message added to django messages framework transaction is successful.
```


[django-shop]: https://github.com/awesto/django-shop
