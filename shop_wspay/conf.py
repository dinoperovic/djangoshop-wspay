# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class DefaultSettings(object):
    """
    Default settings for Shop Wspay.
    """
    def _setting(self, name, default=None):
        from django.conf import settings
        return getattr(settings, name, default)

    @property
    def SHOP_WSPAY_SHOP_ID(self):
        """
        WSPay shop ID.
        """
        from django.core.exceptions import ImproperlyConfigured

        value = self._setting('SHOP_WSPAY_SHOP_ID')
        if not value:
            raise ImproperlyConfigured("SHOP_WSPAY_SHOP_ID setting must be set")
        return value

    @property
    def SHOP_WSPAY_SECRET_KEY(self):
        """
        WSPay shop ID.
        """
        from django.core.exceptions import ImproperlyConfigured

        value = self._setting('SHOP_WSPAY_SECRET_KEY')
        if not value:
            raise ImproperlyConfigured("SHOP_WSPAY_SECRET_KEY setting must be set")
        return value

    @property
    def SHOP_WSPAY_FORM_URL(self):
        """
        Set to 'https://formtest.wspay.biz/Authorization.aspx' for testing.
        """
        return self._setting('SHOP_WSPAY_FORM_URL', 'https://form.wspay.biz/Authorization.aspx')

    @property
    def SHOP_WSPAY_PAYMENT_VIEW(self):
        """
        Set if a separate payment view should be rendered before sending to GestPay.
        """
        return self._setting('SHOP_WSPAY_PAYMENT_VIEW', False)

    @property
    def SHOP_WSPAY_CART_URL(self):
        """
        Url of a cart, used to redirect in some cases.
        """
        fallback = self._setting('SHOP_CART_URL', 'shop:cart-list')
        return self._setting('SHOP_WSPAY_CART_URL', fallback)

    @property
    def SHOP_WSPAY_THANK_YOU_URL(self):
        """
        Thank you url, if None latest order is used.
        """
        fallback = self._setting('SHOP_THANK_YOU_URL')
        return self._setting('SHOP_WSPAY_THANK_YOU_URL', fallback)

    @property
    def SHOP_WSPAY_COMMISION_PERCENTAGE(self):
        """
        Set to add commision percentage for purchase via GestPay.
        """
        return self._setting('SHOP_WSPAY_COMMISION_PERCENTAGE')

    @property
    def SHOP_WSPAY_MODIFIER_CHOICE_TEXT(self):
        """
        Text displayed as a choice for selecting GestPay payment.
        """
        return self._setting('SHOP_WSPAY_MODIFIER_CHOICE_TEXT', 'Wspay')

    @property
    def SHOP_WSPAY_ERROR_MESSAGE(self):
        """
        Message added to django messages framework if there's a transaction error.
        """
        return self._setting('SHOP_WSPAY_ERROR_MESSAGE')

    @property
    def SHOP_WSPAY_CANCEL_MESSAGE(self):
        """
        Message added to django messages framework if transaction is canceled.
        """
        return self._setting('SHOP_WSPAY_CANCEL_MESSAGE')

    @property
    def SHOP_WSPAY_SUCCESS_MESSAGE(self):
        """
        Message added to django messages framework transaction is successful.
        """
        return self._setting('SHOP_WSPAY_SUCCESS_MESSAGE')

    def __getattr__(self, key):
        if not key.startswith('SHOP_WSPAY_'):
            key = 'SHOP_WSPAY_{0}'.format(key)
        return getattr(self, key)


app_settings = DefaultSettings()
