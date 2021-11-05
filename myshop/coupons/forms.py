from django import forms
from django.utils.translation import gettext_lazy as _


class CouponApplyForm(forms.Form):
    """ФОрма для ввода кода купона"""

    code = forms.CharField(label=_('Coupon'))
