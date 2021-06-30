from django import forms
from .models import Item, Images, Category, SubCategory


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
    ('C', 'COD')
)

LABEL_CHOICES = (
    ('N', 'New'),
    ('U', 'Used')
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


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    email = forms.EmailField()


class CreateItemForm(forms.ModelForm):

    title = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        "aria-describedby": "helpId",
        'rows': 1
    }))
    description = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        'rows': 5
    }))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter number'
    }))
    condition_number = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nhập Condition/Vd: 9,8,...'
    }))
    image = forms.ImageField(required=False)

    class Meta:
        model = Item
        fields = ('title', 'price', 'category',
                  'description', 'quantity', 'condition_number', 'size', 'image')


class ImageForm(CreateItemForm):
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta(CreateItemForm.Meta):
        fields = CreateItemForm.Meta.fields + ('images', )
