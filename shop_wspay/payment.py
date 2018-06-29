# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import hashlib
import logging
from distutils.version import LooseVersion

from django.conf.urls import url
from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django_fsm import transition
from shop import __version__ as SHOP_VERSION
from shop.models.address import ISO_3166_CODES
from shop.models.cart import CartModel
from shop.models.order import OrderModel, OrderPayment
from shop.payment.base import PaymentProvider
from shop_wspay.forms import WSPayForm
from shop_wspay.conf import app_settings

logger = logging.getLogger(__name__)


class WSPayPayment(PaymentProvider):
    namespace = 'wspay'

    def get_urls(self):
        return [
            url(r'^$', self.payment_view, name='payment'),
            url(r'^return/$', self.return_view, name='return'),
            url(r'^error/$', self.error_view, name='error'),
            url(r'^cancel/$', self.cancel_view, name='cancel'),
        ]

    def get_payment_request(self, cart, request):
        """
        Redirect to `payment_view` or directly post to WSPay.
        """
        if app_settings.PAYMENT_VIEW:
            return 'window.location.href="%s";' % reverse('shop:%s:payment' % self.namespace)

        try:
            cart.update(request)
            assert cart.extra.get('payment_modifier') == self.namespace
            assert cart.total > 0
        except AssertionError:
            return redirect(app_settings.CART_URL)

        form = WSPayPayment.get_form(cart, request)
        return form.get_js_expression()

    @classmethod
    def get_form(cls, cart, request):
        """
        Returns a form for the current cart do submited or presented to the
        customer in a payment view.
        """
        cart_id = str(cart.id)

        # Split the order total by a decimal point and remove all dots
        # and commas that might be used in a tousand separator.
        assert cart.total.currency == 'HRK', "Currency need's to be in HRK"
        total_amount = '{:.2f}'.format(cart.total.as_decimal()).rsplit('.', 1)
        total_amount[0] = total_amount[0].replace(',', '').replace('.', '')
        signature_total_amount = ''.join(total_amount)
        total_amount = ','.join(total_amount)  # Add a comma as a decimal separator.

        signature_str = '{shop_id}{secret_key}{shopping_cart_id}{secret_key}{total_amount}{secret_key}'.format(
            shop_id=app_settings.SHOP_ID,
            secret_key=app_settings.SECRET_KEY,
            shopping_cart_id=cart_id,
            total_amount=signature_total_amount,
        )
        signature = hashlib.md5()
        signature.update(signature_str)
        signature = signature.hexdigest()

        name_bits = cart.billing_address.name.split(' ')
        first_name = name_bits[0]
        last_name = ' '.join(name_bits[1:]) if len(name_bits) > 1 else ''

        data = {
            'ShopID': app_settings.SHOP_ID,
            'ShoppingCartID': cart_id,
            'TotalAmount': total_amount,
            'Signature': signature,
            'ReturnURL': request.build_absolute_uri(reverse('shop:%s:return' % cls.namespace)),
            'CancelURL': request.build_absolute_uri(reverse('shop:%s:cancel' % cls.namespace)),
            'ReturnErrorURL': request.build_absolute_uri(reverse('shop:%s:error' % cls.namespace)),
            # Extra fields.
            'Lang': request.LANGUAGE_CODE[:2].upper(),
            'CustomerFirstName': first_name,
            'CustomerLastName': last_name,
            'CustomerAddress': cart.billing_address.address1,
            'CustomerCity': cart.billing_address.city,
            'CustomerZIP': cart.billing_address.zip_code,
            'CustomerCountry': dict(ISO_3166_CODES).get(cart.billing_address.country, cart.billing_address.country),
            'CustomerEmail': request.customer.email,
            'CustomerPhone': request.customer.phone_number,
        }
        return WSPayForm(initial=data)

    @classmethod
    @method_decorator(never_cache)
    def payment_view(cls, request):
        """
        View that handles payment if PAYMENT_VIEW setting is True.
        Here is where the customer get's to take a final look at the cart
        before completing the purchase.
        """
        try:
            assert app_settings.PAYMENT_VIEW is True
            cart = CartModel.objects.get_from_request(request)
            cart.update(request)
            assert cart.extra.get('payment_modifier') == cls.namespace
            assert cart.total > 0
        except (CartModel.DoesNotExist, AssertionError):
            return redirect(app_settings.CART_URL)

        form = cls.get_form(cart, request)
        return render(request, 'shop_wspay/payment.html', {'form': form, 'cart': cart})

    @classmethod
    @method_decorator(never_cache)
    def return_view(cls, request):
        """
        View that is accessed by the WSPay when the transaction is complete.
        Here the data returned is validated and cart is either converted
        to an order or gets deleted. Depending on the result either success
        or failed template is rendered.
        """
        try:
            data = {
                'ShoppingCartID': int(request.GET['ShoppingCartID']),
                'Success': int(request.GET['Success']),
                'ApprovalCode': request.GET['ApprovalCode'],
                'Signature': request.GET['Signature'],
            }
        except (KeyError, ValueError):
            return redirect(app_settings.CART_URL)

        try:
            cart = CartModel.objects.get(id=data['ShoppingCartID'])
        except CartModel.DoesNotExist:
            msg = "Cart with id %s doesn't exist" % data['ShoppingCartID']
            logger.error(msg)
            raise SuspiciousOperation(msg)

        logger.info(
            'WSPay response: {Success}; '
            'ShoppingCartID: {ShoppingCartID}; '
            'ApprovalCode: {ApprovalCode}; '
            'Signature: {Signature}'.format(**data))

        signature_str = '{shop_id}{secret_key}{shopping_cart_id}{secret_key}{success}{secret_key}{approval_code}{secret_key}'  # noqa
        signature_str = signature_str.format(
            shop_id=app_settings.SHOP_ID,
            secret_key=app_settings.SECRET_KEY,
            shopping_cart_id=data['ShoppingCartID'],
            success=data['Success'],
            approval_code=data['ApprovalCode'],
        )
        signature = hashlib.md5()
        signature.update(signature_str)
        signature = signature.hexdigest()

        # verify the transaction.
        if (data['Success'] != 1 or data['ApprovalCode'] == '' or data['Signature'] != signature):
            cart.empty()
            return render(request, 'shop_wspay/failed.html')

        # If everything is good up to this point, a cart has been paid for.
        # Create an Order.
        order = OrderModel.objects.create_from_cart(cart, request)

        # Handle API change in djangoSHOP v0.11 that requires an additional
        # method call to populate cart items.
        if LooseVersion(SHOP_VERSION) >= LooseVersion('0.11'):
            order.populate_from_cart(cart, request)

        amount_paid = request.GET['Amount'].replace(',', '.')  # Replace comma with dot as a decimal separator.
        order.add_wspay_payment(data['ApprovalCode'], amount_paid)
        order.extra['transaction_id'] = data['ApprovalCode']
        order.save()
        cart.delete()

        if app_settings.SUCCESS_MESSAGE:
            messages.success(request, app_settings.SUCCESS_MESSAGE)
        if app_settings.THANK_YOU_URL:
            return redirect(app_settings.THANK_YOU_URL)
        return HttpResponseRedirect(OrderModel.objects.get_latest_url())

    @classmethod
    @method_decorator(never_cache)
    def error_view(cls, request):
        """
        There has been an error in transaction. Empty the cart and render
        the error template.
        """
        cart = CartModel.objects.get_from_request(request)
        cart.empty()

        if app_settings.ERROR_MESSAGE:
            messages.error(request, app_settings.ERROR_MESSAGE)
        return render(request, 'shop_wspay/error.html')

    @classmethod
    @method_decorator(never_cache)
    def cancel_view(cls, request):
        """
        Order has been canceled from within the WSPay interface. Empty the
        cart and render the cancel template.
        """
        cart = CartModel.objects.get_from_request(request)
        cart.empty()

        if app_settings.CANCEL_MESSAGE:
            messages.error(request, app_settings.CANCEL_MESSAGE)
        return render(request, 'shop_wspay/cancel.html')


class WSPayWorkflowMixin(object):
    """
    A workflow mixin to add transitons for WSPay payment.
    """
    TRANSITION_TARGETS = {
        'paid_with_wspay': _('Paid using WSPay'),
    }

    def is_fully_paid(self):
        return super(WSPayWorkflowMixin, self).is_fully_paid()

    @transition(field='status', source=['created'], target='paid_with_wspay', custom=dict(admin=False))
    def add_wspay_payment(self, transaction_id, amount):
        """
        Adds a payment object to the order for the given WSPay handler.
        """
        assert self.currency == 'HRK', "Currency need's to be in HRK"
        OrderPayment.objects.create(
            order=self,
            amount=amount,
            transaction_id=transaction_id,
            payment_method=WSPayPayment.namespace,
        )

    @transition(
        field='status', source='paid_with_wspay', conditions=[is_fully_paid],
        custom=dict(admin=True, button_name=_('Acknowledge Payment')))
    def acknowledge_wspay_payment(self):
        """
        Acknowledge payment when the order has been paid with WSPay.
        """
        self.acknowledge_payment()
