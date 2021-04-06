from django import forms


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
    ('C', 'COD')
)


class CheckoutForm(forms.Form):
    # first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
    #     'class': 'form-control form-control-lg',
    #     'type': 'text',
    #     'placeholder': 'Enter your first name',
    #     'disabled': True
    # }))
    # last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
    #     'class': 'form-control form-control-lg',
    #     'type': 'text',
    #     'placeholder': 'Enter your last name',
    #     'disabled': True
    # }))
    # email = forms.EmailField(max_length=100, widget=forms.TextInput(attrs={
    #     'class': 'form-control form-control-lg',
    #     'type': 'text',
    #     'placeholder': 'Enter your email',
    #     'disabled': True
    # }))
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'text',
        'placeholder': 'Enter your phone number'
    }))
    street_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'text',
        'placeholder': 'House number and street name'
    }))
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'text',
        'placeholder': 'Enter your city'
    }))
    district = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'text',
        'placeholder': 'Enter your district'
    }))
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Enter your coupon",
        'type': "text"
    }))
