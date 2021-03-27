from django import forms
from .models import BillingAddress


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
    ('C', 'COD')
)


class CheckoutForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'text',
        'placeholder': 'Enter your first name',
        'disabled': True
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'text',
        'placeholder': 'Enter your last name',
        'disabled': True
    }))
    email = forms.EmailField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'text',
        'placeholder': 'Enter your email',
        'disabled': True
    }))
    phone_number = forms.CharField(max_length=12, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'text',
        'placeholder': 'Enter your phone number'
    }))
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

    class Meta:
        model = BillingAddress
        fields = ['stress_address', 'subregion', 'region']

    def __init__(self, *args, **kwargs):
        super(CheckoutForm, self).__init__(*args, **kwargs)

        self.fields['region'].widget.attrs\
            .update({
                'class': 'form-control',
                'data-width': 'fit',
                'data-style': 'form-control form-control-lg',
            })
        self.fields['subregion'].widget.attrs\
            .update({
                'class': 'form-control',
                'data-width': 'fit',
                'data-style': 'form-control form-control-lg',
            })

