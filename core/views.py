from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import CheckoutForm
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, BillingAddress


class CheckoutView(View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        print(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                print(form.cleaned_data)
                phone_number = form.cleaned_data.get('phone_number')
                region = form.cleaned_data.get('region')
                subregion = form.cleaned_data.get('subregion')
                street_address = form.cleaned_data.get('street_address')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    phone_number=phone_number,
                    stress_address=stress_address,
                    region=region,
                    subregion=subregion
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                return redirect('core:checkout')
            messages.warning(self.request, "Fail checkout")
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'payment.html')


class HomeView(ListView):
    model = Item
    template_name = 'index.html'


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('/')


class ShopView(ListView):
    model = Item
    template_name = 'shop.html'
    paginate_by = '12'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'detail.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
        else:
            messages.info(request, "This item was added to your cart.")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date
        )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.warning(request, "This item was removed from your cart.")
        else:
            # add a message saying the order doesn't contain the item
            messages.warning(request, "This item was not in your cart.")
            HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        # add a message saying the user doesn't have an order
        messages.warning(request, "You do not have an active order.")
        HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.warning(request, "This item quantity was updated.")
        else:
            # add a message saying the order doesn't contain the item
            messages.warning(request, "This item was not in your cart.")
            HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        # add a message saying the user doesn't have an order
        messages.warning(request, "You do not have an active order.")
        HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
