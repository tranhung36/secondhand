from django.urls import path
from .views import (
    HomeView,
    ItemDetailView,
    ShopView,
    CartView,
    CheckoutView,
    PaymentView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    AddCouponView,
    RequestRefundView,
    ItemCategoryView,
    create_product
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('create-product/', create_product, name='create-product'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('shop/category/<slug>/', ItemCategoryView.as_view(), name='category')
]
