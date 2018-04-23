# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from shop_wspay.conf import app_settings


class WSPayForm(forms.Form):
    """
    A base form with required fields for WSPay integration.
    """
    ShopID = forms.CharField(widget=forms.HiddenInput)
    ShoppingCartID = forms.CharField(widget=forms.HiddenInput)
    TotalAmount = forms.CharField(widget=forms.HiddenInput)
    Signature = forms.CharField(widget=forms.HiddenInput)
    ReturnURL = forms.CharField(widget=forms.HiddenInput)
    CancelURL = forms.CharField(widget=forms.HiddenInput)
    ReturnErrorURL = forms.CharField(widget=forms.HiddenInput)
    # Extra fields
    Lang = forms.CharField(widget=forms.HiddenInput)
    CustomerFirstName = forms.CharField(widget=forms.HiddenInput)
    CustomerLastName = forms.CharField(widget=forms.HiddenInput)
    CustomerAddress = forms.CharField(widget=forms.HiddenInput)
    CustomerCity = forms.CharField(widget=forms.HiddenInput)
    CustomerZIP = forms.CharField(widget=forms.HiddenInput)
    CustomerCountry = forms.CharField(widget=forms.HiddenInput)
    CustomerEmail = forms.CharField(widget=forms.HiddenInput)
    CustomerPhone = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(WSPayForm, self).__init__(*args, **kwargs)
        self.action = app_settings.FORM_URL

    def get_js_expression(self):
        def js_fields_generator():
            for name in self.fields:
                yield """
                    var {name} = document.createElement('input');
                    {name}.setAttribute('type', 'hidden');
                    {name}.setAttribute('name', '{name}');
                    {name}.setAttribute('value', '{value}');
                    form.appendChild({name});""".format(name=name, value=self[name].value())
        js_fields = ''.join([x for x in js_fields_generator()])
        js_expression = """
            (function () {{
              var form = document.createElement('form');
              form.setAttribute('action', '{action}');
              form.setAttribute('method', 'POST');
              {js_fields}
              document.body.appendChild(form);
              form.submit();
            }})();""".format(action=self.action, js_fields=js_fields)
        return js_expression.replace('  ', '').replace('\n', '')
